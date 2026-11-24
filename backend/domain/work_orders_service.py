from core.records import get, insert, need, update
from domain.jigs_model import jigs
from domain.coupons_model import coupons
from domain.profiles_model import profiles
from domain.work_orders_model import work_orders

# 多片委托状态机
WAIT_FIRST = '待首片签回'     # 多片委托已占机位，等待复核员签首片冷却弯度
WAIT_REMAIN = '待余片开工'     # 首片已签，等待行程上界通过弯模当前行程
IN_PROGRESS = '余片开工'       # 余片已开工，行程与放行依据已固化
DONE_PREFIX = '已打样 '        # 整片签回完成；单片委托沿用此前简单流程

def book_jig(conn, user, data):
    profile = get(conn, profiles, data.profile)
    coupon = get(conn, coupons, profile['coupon'])
    jig = get(conn, jigs, data.jig, lock=True)
    need(jig['calibrated'], '该机位弯模尚未检定')
    need(max(profile['prediction'], coupon['target']) <= jig['max_throw'], '夹具有效行程不足，机位未占用')
    need(1 <= data.quantity <= 20, '本炉试片数超额')
    # 多片委托先打一片再开余片；单片委托仍走一次签回的简单流程
    state = WAIT_FIRST if data.quantity > 1 else '待打样'
    return insert(conn, work_orders, **data.model_dump(), state=state)


def sign_first(conn, user, data):
    # 与弯模重校并发：统一先锁弯模再锁委托，先办成者决定后续判定
    order = get(conn, work_orders, data.order)
    jig = get(conn, jigs, order['jig'], lock=True)
    order = get(conn, work_orders, data.order, lock=True)
    need(order['quantity'] > 1, '单片委托无需首片签回，直接签回打样见证')
    # 余片开工前允许重签首片（上界不达标时可重测重签）；开工后即固化
    need(order['state'] in (WAIT_FIRST, WAIT_REMAIN), '委托已离开首片签注阶段')
    need(data.bend >= 0, '首片冷却弯度不能为负')
    profile = get(conn, profiles, order['profile'])
    # 用首片实弯与签注预测的偏差修正余片预测，再加曲线留出 MAE 作行程上界
    bias = data.bend - profile['prediction']
    revised = profile['prediction'] + bias
    bound = revised + profile['mae']
    # 首片签回重试不重复计数：首次签回记 1，之后重试保持不变
    attempts = 1 if order['first_attempts'] is None else order['first_attempts']
    return update(conn, work_orders, data.order, state=WAIT_REMAIN, first_bend=data.bend,
        first_attempts=attempts, revised_prediction=round(revised, 3), travel_bound=round(bound, 3))


def start_remain(conn, user, data):
    # 余片开工与弯模重校并发：先锁弯模再锁委托，先办成者生效
    order = get(conn, work_orders, data.order)
    jig = get(conn, jigs, order['jig'], lock=True)
    order = get(conn, work_orders, data.order, lock=True)
    need(order['state'] == WAIT_REMAIN, '委托尚未进入余片开工阶段')
    # 未签首片时 travel_bound 为空；这里以状态兜底并给出明确拦截
    need(order['first_bend'] is not None and order['travel_bound'] is not None, '首片尚未签回，余片不开工')
    need(jig['calibrated'], '弯模量具已失校，余片不开工')
    need(order['travel_bound'] <= jig['max_throw'],
         f'行程上界 {order["travel_bound"]} mm 超出弯模当前行程 {jig["max_throw"]} mm，余片不开工')
    # 开工后保留当时的行程和放行依据，随后的重校不再影响本单
    basis = {
        'profile': order['profile'],
        'first_bend': order['first_bend'],
        'revised_prediction': order['revised_prediction'],
        'mae': get(conn, profiles, order['profile'])['mae'],
        'travel_bound': order['travel_bound'],
        'jig_throw_at_release': jig['max_throw'],
    }
    return update(conn, work_orders, data.order, state=IN_PROGRESS,
        release_throw=jig['max_throw'], release_basis=basis)


def complete(conn, user, data):
    order = get(conn, work_orders, data.order, lock=True)
    need(data.witness.startswith('W-'), '见证号需使用 W- 前缀')
    if order['quantity'] > 1:
        # 多片委托：余片开工并签回才算整单完成
        need(order['state'] == IN_PROGRESS, '余片尚未开工，整单不能签回')
    else:
        need(order['state'] == '待打样', '委托已经签回')
    return update(conn, work_orders, data.order, state=DONE_PREFIX + data.witness)
