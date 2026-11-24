        import {workspace} from '../workspace.js';
        import {el} from '../dom.js';

        const page = {
  "title": "试制机位与打样见证",
  "module": "试制工位委托",
  "caption": "试制工位委托",
  "detail": "多片委托先打一片：复核员签首片冷却弯度，按与签注预测的偏差修正余片预测，再加曲线留出误差作行程上界；上界不超弯模当前行程才开余片，开工后固化当时行程与放行依据。",
  "path": "/work_orders",
  "columns": [
    {
      "name": "code",
      "label": "编号"
    },
    {
      "name": "profile",
      "label": "依据"
    },
    {
      "name": "jig",
      "label": "工位弯模"
    },
    {
      "name": "slot",
      "label": "机位时段"
    },
    {
      "name": "quantity",
      "label": "试片数"
    },
    {
      "name": "state",
      "label": "状态"
    },
    {
      "name": "first_bend",
      "label": "首片冷却弯度 mm"
    },
    {
      "name": "first_attempts",
      "label": "首片签回次数"
    },
    {
      "name": "revised_prediction",
      "label": "修正预测 mm"
    },
    {
      "name": "travel_bound",
      "label": "行程上界 mm"
    },
    {
      "name": "release_throw",
      "label": "开工时行程 mm"
    },
    {
      "name": "release_basis",
      "label": "放行依据"
    }
  ],
  "layout": "flip",
  "view": "table",
  "actions": [
    {
      "name": "book_jig",
      "label": "分配机位",
      "path": "/work_orders/book-jig",
      "fields": [
        {
          "name": "code",
          "label": "委托号",
          "kind": "text",
          "initial": "JOB-24"
        },
        {
          "name": "profile",
          "label": "曲线版本",
          "kind": "text",
          "initial": "PRO-11"
        },
        {
          "name": "jig",
          "label": "工位弯模",
          "kind": "text",
          "initial": "CL-44"
        },
        {
          "name": "slot",
          "label": "唯一机位时段",
          "kind": "text",
          "initial": "11-24 15:30"
        },
        {
          "name": "quantity",
          "label": "试片数",
          "kind": "int",
          "initial": 3
        }
      ],
      "help": "多片委托（试片数大于 1）登记后进入“待首片签回”，先打一片再开余片。",
      "roles": [
        "operator",
        "reviewer"
      ],
      "success": "已写入"
    },
    {
      "name": "sign_first",
      "label": "签首片冷却弯度",
      "path": "/work_orders/sign-first",
      "fields": [
        {
          "name": "order",
          "label": "委托号",
          "kind": "text",
          "initial": "JOB-21"
        },
        {
          "name": "bend",
          "label": "首片冷却弯度 mm",
          "kind": "float",
          "initial": 10.4
        }
      ],
      "help": "用首片实弯与签注预测的偏差修正余片预测，并加曲线留出 MAE 得行程上界。重试不重复计数。",
      "roles": [
        "reviewer"
      ],
      "success": "已写入"
    },
    {
      "name": "start_remain",
      "label": "余片开工",
      "path": "/work_orders/start-remain",
      "fields": [
        {
          "name": "order",
          "label": "委托号",
          "kind": "text",
          "initial": "JOB-21"
        }
      ],
      "help": "行程上界须不超过弯模当前行程。与弯模重校并发时认先办成的；开工后保留当时行程与放行依据。",
      "roles": [
        "reviewer"
      ],
      "success": "已写入"
    },
    {
      "name": "complete",
      "label": "签回打样见证",
      "path": "/work_orders/complete",
      "fields": [
        {
          "name": "order",
          "label": "委托号",
          "kind": "text",
          "initial": "JOB-21"
        },
        {
          "name": "witness",
          "label": "技师见证号",
          "kind": "text",
          "initial": "W-0302"
        }
      ],
      "help": "多片委托须余片开工后签回，才算整单完成。",
      "roles": [
        "reviewer"
      ],
      "success": "已写入"
    }
  ]
};

        export const {title} = page;
        export const key = "work_orders";
        export async function render(root, role) {
          await workspace(root, role, page);

        }
