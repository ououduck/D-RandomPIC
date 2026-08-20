# D-RandomPIC

基于 Cloudflare Pages 404 规则与 GitHub Actions 自动构建的随机图 API。

访问 `https://randompic.pldduck.com/ecy-v` 之类的地址即可获得一张随机图片。

## 工作原理

本项目不依赖任何后端服务，完全由静态文件与 Cloudflare 规则实现随机取图：

1. `gen_pic.py` 扫描 `pic/` 下的分类子文件夹，将每个分类的图片复制到 `dist/<分类>/` 目录下，并按十六进制编号重命名，生成 `000.jpg` 到 `fff.jpg` 共 4096 个文件（对应规则中 3 位十六进制 hash 的全部取值，覆盖所有可能路径，保证不会 404）。
2. 构建产物 `dist/` 部署到 Cloudflare Pages。
3. 在 Cloudflare 为该 Pages 项目配置 404 规则（见 `rule.txt`）：

   ```
   concat(http.request.uri.path, "/", substring(uuidv4(cf.random_seed), 0, 3), ".jpg")
   ```

   当用户访问 `/ecy-v` 时，如果该路径不存在（返回 404），规则会使用随机种子生成 3 位十六进制字符串并重写到 `/ecy-v/xxx.jpg`，从而随机返回该分类下的一张图片。

## 目录结构

```
D-RandomPIC/
├── gen_pic.py            # 构建脚本：生成 dist/ 下的随机图片文件
├── index.html            # 演示页面（列出各分类 API 地址）
├── 404.html              # 404 响应体
├── rule.txt              # Cloudflare 404 规则表达式
├── pic/                  # 源图片目录（按分类存放）
│   ├── ecy-h/            # 随机二次元图（横屏/电脑）
│   ├── ecy-v/            # 随机二次元图（竖屏/手机）
│   ├── fj/               # 其他分类示例
│   └── ys/               # 其他分类示例
└── dist/                 # 构建产物（由 gen_pic.py 生成，不提交到仓库）
```

新增图片分类时，只需在 `pic/` 下新建一个子文件夹并放入图片，推送到仓库即可，构建脚本与 Cloudflare 规则无需改动。

## 本地构建

需要 Python 3（仅使用标准库，无需安装任何依赖）。

```bash
python gen_pic.py
```

构建完成后检查 `dist/` 目录，每个分类下应生成 4096 个文件（`000.jpg` 到 `fff.jpg`）。

## 部署到 Cloudflare Pages

### 1. 创建 Pages 项目

在 Cloudflare Dashboard 中创建 Pages 项目（选择 "Direct Upload" 即可，构建由 GitHub Actions 完成），记录项目名称（例如 `d-randompic`）。

### 2. 配置 404 规则

在 Pages 项目的自定义域或对应 Zone 的 Rules 中，为 404 状态码配置重写规则，表达式见 `rule.txt`：

```
concat(http.request.uri.path, "/", substring(uuidv4(cf.random_seed), 0, 3), ".jpg")
```

### 3. 配置 GitHub Actions Secrets

在仓库 Settings -> Secrets and variables -> Actions 中配置：

| 名称 | 说明 |
| --- | --- |
| `CLOUDFLARE_API_TOKEN` | Cloudflare API Token，需具备 Pages 编辑权限 |
| `CLOUDFLARE_ACCOUNT_ID` | Cloudflare 账号 ID（Dashboard 首页右下角可查看） |

> 可选：若 Pages 项目名不是 `d-randompic`，可在仓库的 Variables 中新增 `CLOUDFLARE_PROJECT_NAME` 并填入实际项目名；workflow 会优先使用该变量。

## 自动构建与部署

`.github/workflows/deploy.yml` 中的 GitHub Actions 会在每次提交（push）后自动执行：

1. 检出代码；
2. 运行 `gen_pic.py`，生成 `dist/` 构建产物；
3. 将 `dist/` 部署到 Cloudflare Pages。

之后访问 `https://randompic.pldduck.com/<分类名>` 即可随机获取对应分类的图片。

## API 使用

- `GET /ecy-v`：随机二次元图（竖屏/手机）
- `GET /ecy-h`：随机二次元图（横屏/电脑）
- 新增分类 `xxx` 后，`GET /xxx` 即生效

示例：

```bash
curl -L https://randompic.pldduck.com/ecy-v
```

在 HTML 中直接使用：

```html
<img src="https://randompic.pldduck.com/ecy-v" alt="随机图片">
```

## 许可证

[MIT](LICENSE)
