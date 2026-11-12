# A04 智慧党建项目

## 直接查看

双击 **`智慧党建.html`** 即可在浏览器中打开，不需要安装依赖、不需要启动服务器。

- 测试账号：`13094698024`
- 密码：`123456`
- 该 HTML 已内联全部 JS、CSS 和图片（约 12 MB），可单独发给别人。
- 涉及后端接口的功能（AI 问答、知识库上传、注册等）在未启动后端时会提示服务不可用，这是正常的。

## 源码

源码位于 `src-2/src-2/`。

```bash
cd src-2/src-2
npm install        # 首次运行或删除 node_modules 后需要
npm run dev        # 开发服务器，默认 http://localhost:5173
npm run build:single   # 重新生成单文件 dist-single/index.html
```

生成单文件后，把 `dist-single/index.html` 复制到项目根目录并改名为 `智慧党建.html` 即可。

## Mock 后端（可选）

```bash
cd src-2/src-2/backend
pip install -r requirements.txt
python app.py      # http://localhost:5000
```

Mock 后端只实现了 `/agent/*`、`/qa/*` 等少量接口；登录注册、知识库接口需要接入真实的统一服务（接口文档见 `src-2/src-2/api/接口文档.md`）。
