# Duke Humanoid V2 硬件站 —— 设计说明

写给维护这个站的人，不是写给读者的。读者看 `docs/`；你要改这个站之前，先看这份。

内容：为什么是这个信息架构、四个对标各贡献了什么、BOM 为什么由 CSV 驱动、
装配步骤页的模板长什么样、怎么加一步、将来硬件改版怎么用 mike 做版本化、
以及这个站对外公开之前团队必须先交出来的东西。

---

## 0. 这个站的唯一目标

**一个跟我们无关的人读完，能造出一台一模一样的机器。**

这一句决定了后面每一个设计选择。它有两个推论，整个站都建立在这两条上：

1. **软件不在这里。** 代码、权重、训练、部署已经开源，`docs/software.md` 只是一座桥。
   把软件文档抄进来的唯一结果是两份文档互相漂移。
2. **没有的东西必须看得见。** 这个站今天造不出机器人——CAD 没发、紧固件表不存在、
   扭矩一个都没有、license 没声明。这些不是藏起来慢慢补，而是首页第一屏就写清楚，
   每一处缺口在原地留一个带负责人的 TODO 块，再汇总成
   [`docs/reference/todo.md`](docs/reference/todo.md) 这张 178 行的工单表。

   **一份诚实的残缺文档比一份自信的错误文档有用得多。** 一个读者知道扭矩没有，
   他会去问；一个读者读到我们编的扭矩，他会去拧。这台机器 36 kg。

---

## 1. 信息架构：为什么是这八节

nav 的顺序 = **一个人真实的工作顺序**，不是我们内部的组织结构：

```
决定要不要做 → 买什么 → 做什么 → 怎么装 → 怎么接线 → 怎么点亮 → 查资料
Before you start → BOM → Fabrication → Assembly → Electrical → Bring-up → Reference
```

几条具体的取舍：

**Before you start 排第一，Safety 又排在它的第一。**
这台机器 36 kg、31 个准直驱关节、两组 6S 锂电，而且**所有关节都没有自锁减速器**——
断电（包括急停）不会把机器人停在原地，它会塌下来。运维手册自己写的是
"drives a 36 kg humanoid with people beside it"。所以顺序是先劝退、再花钱。
首页 "Where to start" 那一行明确写着 *Do not order parts first*。

**BOM 排在 Fabrication 前面，Fabrication 排在 Assembly 前面。**
机加工是全程最长的那根杆子。读者应该先把 63 件的报价发出去，等的时候再去读别的。
`bom/sourcing.md` 存在的理由就是这个。

**Electrical 是独立一节，不是 Assembly 的子节。**
这是一个已知有风险的决定，写在这里以便将来推翻：线束很可能必须在肢体合拢**之前**
预穿进去。如果第一次真实装配证实了这一点，Electrical 就必须和 Assembly 交错，
而不是排在它后面。`electrical/harness-fabrication.md` 已经提出这个要求，
对应的 TODO 挂在 `assembly/index.md`。**这是整份 IA 里最可能需要改的一处。**

**Software 只有一页。** 它是桥，不是章。

**Reference 不是一个阶段，是查阅区。** 全规格表、零件号索引、修订策略、故障排查、
FAQ、引用与许可，加上团队自己的工单表。

**每一节都有 `index.md`。** `navigation.indexes` 打开着，所以点顶部标签直接落到该节
的导览页，不会落到一个随机子页。每个导览页的职责是：这一节回答什么问题、
读完能做什么、以及**这一节今天缺什么**。

### 一个刻意没做的事

没有按"左腿/右臂/云台"给 BOM 分文件。源表本身就没有这个维度（它只有
ELECTRONICS / HARDWARE / MATERIALS 三组），硬拆会是猜。
真实的分组走 `cnc-parts.csv` 的 `subassembly` 列，
`bom_subtotal("cnc-parts.csv", subassembly="leg")` 随时能算出一条腿的机加工成本。
**数据分列，不分文件**——加一个视角不需要改数据布局。

---

## 2. 四个对标各自贡献了什么

结论先说：**没有任何一个项目值得整体照抄**，四个都在某个维度不及格。
逐维度挑最好的那个，是这个站唯一可行的做法。

| 项目 | 我们抄了什么 | 我们为什么不抄它的其余部分 |
|---|---|---|
| **Menlo Asimov 1** | 装配步骤页的形态：83 个编号步骤页，每页顶部一张 "Parts needed"（Part \| Count）表（78/83 页都有）；螺纹胶**只在准备页点一次牌号**，步骤页一律只写 `Threadlocker \| As needed` | 全站 136 页 **0 次出现 "license"**——CAD 能下载，法律上却不可衍生。也没有任何价格。它的 3D 播放器（431 个指令态）成本太高，我们用静态渲染代替 |
| **OpenArm 1.0** | BOM 按子装配 × 制造类别分页、带型号/单价/总价；每步一张**只高亮被连接零件**的渲染；**每个子装配页开头的阻塞式警告**，强制先配好电机 ID（我们有六条 CAN 总线，更需要） | 2.0 把 CAD 退回成 Google Drive 裸链接，装配文档直接没了；`removedInV2` 式静默重定向会让拿着新硬件的人读到旧文档而不被告知 |
| **ToddlerBot 2.0** | **成本分档**：本体 / 工具 / 可选三个 tier 分开报（本体 $5,727.94 / 工具 $1,976.13 / 可选 $2,252.73）；五金先分格清点、"最后剩件即说明漏步"的验收协议；螺纹胶给总量（"about 100 颗"） | 硬件 license 是 CC BY-NC-SA 4.0（禁商用），我们不应该跟；CAD 挂 Onshape 活文档，没有版本号 |
| **Berkeley Humanoid Lite** | 工程笔记与复现实验的写法；`.github/workflows/release.yml` 那 57 行 attach-on-tag 是可以直接用的模板 | **反面教材最多**：BOM 是一个 Google Sheet iframe——不能 diff、不能 pin、不能归档；`releases.json` 里两个 tag 的 `assets` 都是空的（机制它自己写好了却没接上）；文档和代码解耦导致 7 条命令里 4 条失效 |

**四个对标全都缺的一样东西：扭矩值。** 四家合起来 0 个 N·m 数字。
所以我们在每一个步骤页都留了一个显式的 torque 字段——这是本站唯一一处
"结构上比所有对标都强"的地方，前提是有人把数填进去。

**最贵的错误都不是技术性的。** Asimov 有全世界最好的装配手册，因为没写 license
而法律上不可复用；Berkeley 把五千美元的论点押在一个不能归档的表格上。
所以本站的两条硬规矩是：**license 是发布阻塞项**，**BOM 必须是仓库里的 CSV**。

---

## 3. BOM 由 CSV 驱动：机制与理由

### 理由

**页面正文里不允许出现任何手打的价格。** 手打的小计在零件重新采购的那一刻就过期了，
而一张会漂移的成本表正是这次发布要修的缺陷本身。

### 机制

```
reference/bom/*.csv  ──tools/gen_*.py──>  docs/data/*.csv  ──main.py 宏──>  页面
    源表（不在仓库里）        生成器           发布数据（在仓库里）      实时计算
```

- `docs/data/*.csv` 是**生成物**，不要手改。改源表，重跑 `tools/gen_*.py`。
  列约定写在 `docs/data/README.md`，生成器说明写在 `tools/README.md`。
- 页面调用 `main.py` 里的宏：`bom_subtotal()` / `bom_total()` / `bom_count()` /
  `bom_qty()` / `bom_unpriced()` / `bom_priced_as_of()` / `data_file_exists()`。
- **CSV 不存在时，宏返回一个可见的 *not yet published* 标记，构建照样通过。**
  这是设计，不是将就：诚实的洞，永远优于编出来的数。

### 三条踩过的坑，写在这里免得再踩

1. **`bom_total()` 必须裸调。**
   曾经有三个页面各自在 `bom_total([...])` 里手写六个文件名。
   第七个零件文件一落地，这三页就会同时错，而且错得互不一致。
   现在裸调 `bom_total()` = 目录下所有**符合零件 schema** 的 CSV，
   减去 `main.py` 里的 `NON_ROBOT_FILES`（测试夹具、工具、选配、备件）。
   这个白名单存在的直接原因：裸调曾经把 `test-fixtures.csv` 扫了进去，
   悄悄把 $101.38 的单腿测试夹具算进了一台机器人的售价。

2. **`read_csv()` 会把数字重新解析。**
   它走 `tabulate`，`"$14,881.99"` 会变成 `14882`，`"217.00"` 会变成 `217`。
   永远传 `dtype="str", keep_default_na=False, disable_numparse=True`，
   而且 `dtype` 必须是**带引号的字符串** `"str"`——裸 `str` 在 Jinja 环境里未定义，
   会直接让构建失败。

3. **`allow_missing_files: false`。**
   `read_csv` 指向不存在的文件 = 硬失败。只有 `bom_*` 宏会优雅降级。
   任何可能还没落地的文件，用 `{% if data_file_exists("x.csv") %}` 包起来。

### 今天的口径

整机零件 `bom_total()` = **$15,231.37**，由六个文件实时算出。
站里在三个地方写明这是一个**下限（floor）**而不是价格：紧固件和打印件全部未计价，
工具、运费、开机费都不在内。源表那个 `$14,881.99` 只作为"**不能用的数字**"出现一次。

---

## 4. 装配步骤页模板

每个子装配一页（leg / arm / torso-and-waist / head-and-camera-gimbal / gripper /
final-integration），页内 7–10 个编号步骤。

**刻意没抄 Asimov 的一步一页。** Asimov 需要 83 页是因为每一步挂一个 3D 播放器；
我们用静态渲染，一页一个子装配可以让整条腿在一个页面里被搜索到。

一步的完整结构：

```markdown
{{ step(3, "Build the hip-roll joint onto the hip") }}

<div class="parts-needed" markdown>

Parts needed

| Part ID | Qty | Description |
| --- | --- | --- |
| Robstride 03 — ID 32 (left) / 42 (right) | 1 | `hip_2` |
| `CNC_leg06_x2_hip_roll_output_shaft` | ? | Hip-roll output shaft |
| Threadlocker | As needed | Grade on [Tools](tools.md) |

</div>

一两段说明这一步真正的难点在哪。

> **Figure** <span class="pending-figure">not produced yet</span> —
> `assets/assembly/leg-step-03.png`: 这张渲染必须显示什么。

!!! warning "TODO — 待填"
    还缺什么，写到有答案的人一看就认领的程度。
    Torque: no N·m value exists for this interface.
    *Owner: hardware lead, from a photographed build.*

{{ checkpoint("这一步做完，必须能验证的那件事。") }}
```

各部分的用意：

- **`{{ step(n, title) }}`** 生成带圆形编号徽章的 `<h3>`，锚点固定为 `#step-n`。
  工单表就是靠这个锚点深链到具体步骤的。
- **Parts needed 表**放在最前面（抄 Asimov）。**`Threadlocker | As needed` 是固定行**，
  牌号只在 `assembly/tools.md` 点一次——避免 83 处牌号将来各改各的。
- **Figure 占位符不能写成真的 `![](…)`。** `mkdocs build --strict` 对不存在的图片
  会直接失败，而且是整站失败。所以用引用块 + `.pending-figure` span 顶着，
  文件落地那天一行换成 `![]()`，同一个 commit 里把 `docs/assets/MANIFEST.md` 的行删掉。
- **TODO 块的 `*Owner:*` 行是强制的。** `tools/gen_punchlist.py` 没有它会直接报错退出。
  没有负责人的 TODO 是愿望，不是工单。
- **`{{ checkpoint(...) }}`** 是必过的验证门，不是一般建议。
  写"能验证什么"，不写"注意什么"。
- **每个子装配页开头有阻塞式警告**，要求先配好 CAN ID（抄 OpenArm）。
  六条总线：`can9` 左臂 / `can21` 右臂 / `can22` 腰 + 两侧肩 pitch /
  `can23` 右腿 / `can24` 左腿 / `can25` 四个相机关节，全部 1 Mbit/s。

---

## 5. 怎么加一个装配步骤

1. 在对应页面的正确位置插入 `{{ step(N, "祈使句标题") }}`。
   **后面所有步骤要重新编号**——编号是写死的参数，不是自动的。
   `#step-N` 锚点会跟着变，所以改完一定要重跑链接检查。
2. 紧跟 Parts needed 表，用 `<div class="parts-needed" markdown>` 包住。
   零件 ID 必须和 `docs/data/*.csv` 里的 `part_id` 一字不差。
   数量未经 CAD 核对就写 `?`，不要猜——今天 63 行源数据里有 25 行的
   `_xN` 和数量列自相矛盾。
3. 写说明。只写这一步真正的难点，不写显而易见的动作。
4. 加 Figure 占位符，路径按 `assets/assembly/<page>-step-NN.png` 命名。
5. 缺的数字全部进 TODO 块，带 `*Owner:*`。
   **一个都不许编**：扭矩、轴承型号、螺钉规格、过盈量、线规。
6. 加 `{{ checkpoint(...) }}`。问自己：这一步装错了，在哪一步会被发现？
   如果答案是"点亮之后"，这个 checkpoint 就必须能在这里就抓住它。
7. 更新页面底部的 figure manifest 表。
8. 重跑：

   ```bash
   python tools/gen_punchlist.py
   python tools/gen_image_manifest.py
   mkdocs build --strict
   ```

   两张汇总表是生成的。不重跑，新步骤的 TODO 就不会出现在团队的工单表里。

---

## 6. 硬件改版怎么做版本化（mike）

`mike` 已经在 `requirements.txt` 里（2.2.0），但**还没有启用**。
现在的站是"一个硬件修订"的站，首页也是这么声明的。
下面是将来 v2.2 出现时的路径，现在不要提前做。

### 为什么硬件必须版本化，而软件不必

软件用户升级；**硬件用户升不了**。一个人按 v2.1 的文档订了 63 个机加工件、
31 个执行器，这些零件就永远是 v2.1 的。文档站原地改成 v2.2，
他手上那台机器就没有文档了。

这也是不能抄 OpenArm 的地方：它的 `removedInV2` 静默重定向会把拿着 1.0 硬件的人
悄悄送到 2.0 的页面，**不告诉他**。宁可让旧版本页面停在原地腐烂，也不要静默重定向。

### 具体怎么接

1. `mkdocs.yml` 里加 version provider：

   ```yaml
   extra:
     version:
       provider: mike
       default: v2.1
   ```

2. CI 的部署步骤从 `mkdocs gh-deploy` 换成 `mike deploy --push --update-aliases`。
   第一次：

   ```bash
   mike deploy --push --update-aliases v2.1 latest
   mike set-default --push latest
   ```

3. 改版时：

   ```bash
   mike deploy --push --update-aliases v2.2 latest   # latest 指向新版
   ```

   `v2.1` 原地冻结，URL 永久有效，右上角出现下拉选择器。

### 三条规矩

- **修订号 = 机器人的硬件修订号，不是文档的版本号。** 今天的候选是 `humanoid_v21`
  （`reference/revisions.md` 上有一个 TODO 要求确认它到底是不是）。
  文档措辞改一下不是新版本。
- **什么算 bump：** 任何让旧文档装不出新机器的改动——机加工件几何变了、
  执行器换型号了、CAN 拓扑变了、紧固件规格表变了。`reference/revisions.md`
  上有一个 TODO 要求把这条规则写死。
- **每次 bump 必须配一页迁移说明**：改了什么、旧零件还能不能用、
  已经装好一台的人要不要动。抄 OpenArm 的版本化，不抄它的静默重定向。

### 先决条件

版本化之前，三个仓库必须先打得出 tag 并 cut 出 release，
把代码 + 资产 + CAD 一起 pin 住。今天三个仓库**一个 tag 都没有**，
所以任何人都无法把自己的构建 pin 到一个已知状态。
这是 `reference/revisions.md` 上的一条 TODO，也是 mike 的真正前置条件。

---

## 7. 公开之前团队必须先交出来的东西

首页那个 danger 横幅列了六条，那是对读者的说法。下面是对内的说法，
按"不给就不能叫 open-source hardware release"排序。
完整的 178 条在 [`docs/reference/todo.md`](docs/reference/todo.md)，
其中 40 条被标记为阻塞发布。

### 硬阻塞（没有这些就不该发）

| # | 要交的东西 | 谁 | 为什么是阻塞 |
|---|---|---|---|
| 1 | **三段 license：代码 Apache-2.0 / 硬件 CERN-OHL-W 或 -S / 文档 CC-BY-4.0** | PI + 学校技转办 | Apache-2.0 只覆盖代码。**今天没有任何人被授权制造这些零件。** Asimov 就是栽在这一条上的：136 页文档、CAD 可下载、法律上不可衍生。站里只陈述了 -W 与 -S 的取舍，没有替你们选 |
| 2 | **机器人 CAD**：机加工件 STEP + 打印件 STL/3MF，挂在打了 tag 的 GitHub Release 上 | 硬件负责人 | 仓库里现有的 3 个 `.step` 全是感知标定夹具，一个机器人零件都没有。仿真网格不是制造几何——没有公差、没有螺纹、没有表面处理 |
| 3 | **紧固件表**：螺纹、螺距、长度、头型、驱动、材质、表面、数量，加轴承、定位销、螺纹胶牌号 | 硬件负责人，从 CAD 导 | 今天整机所有五金是**一行占位符**。它同时卡住每一个装配页和任何一个诚实的整机成本 |
| 4 | **扭矩值 + 螺纹胶牌号** | 硬件负责人，从一次拍了照的装配 | 四个对标全缺这一项，是我们唯一能直接超过所有人的地方；同时它是读者"再读仔细一点"也补不上的空白 |
| 5 | **电池组拓扑：串联还是并联** | 电气负责人 | 决定母线是 44.4 V 还是 22.2 V。站里列了四条证据指向串联（两组 6S 一起买、两个 48 V 标称的转换器、一个 20–60 V 转换器、一个 53 V standoff 的 TVS），并**明确标注为证据而非规格**。整个 Electrical 节都压在这一条上。**不要用推断把它关掉** |
| 6 | **硬件急停** | 电气负责人 + 安全签字 | 全仓库 grep 不到任何急停、主断路、保险、断路器、预充或钥匙开关。一台 36 kg、31 个执行器、两组 6S 的机器，唯一的"停"是电机环里的一个软件限速。**这是整份文档里最严重的一条** |
| 7 | **人身安全程序**：断电塌落行为、吊装点与吊具、旁观者距离、上下电顺序、锂电充电与处置 | 硬件负责人 + 学校 EHS | 运维手册自己写着 "36 kg humanoid with people beside it" |
| 8 | **打印参数** `docs/data/print_profiles.csv` | 硬件负责人，从当初切片的 profile 导 | 文件一落地，`fabrication/printing-guide.md` 的整张表自动渲染出来 |

### 强烈建议在发布时就有

- **零件编号定案。** 源表 63 行里三套方案并存：36 个 `CNC_*`（其中一件重复两次，
  去重后 35）、22 个 `NN_*` 疑似单腿测试台遗留、5 个 `B` 系列（没有 B4，
  B6 是测试夹具已移出整机）。所以**63 行不等于 63 个不同零件**，
  很可能有同一个零件挂着两套编号——两套都订大约会让机加工费翻倍。
  定一套方案，然后从 CAD 生成 `reference/part-index.md`，不要手写。
- **63 个机加工件的材料 / 公差 / 表面处理 / 供应商。** 今天 63 行在这四列上**全空**。
- **两个供应风险件的替代料**：RealSense D436、每一个 Robstride 型号。今天零替代。
- **`priced_as_of`**：今天每一行都空，所以全站的 `bom_priced_as_of()` 都显示
  *not yet published*。任何价格对外引用之前，先重新核价并打上日期。
- **`tools.csv` 与 `optional.csv`**：工具档和选配档（那个约 $600 的第三相机模块属于选配）。
- **图**：157 张。清单在 [`docs/assets/MANIFEST.md`](docs/assets/MANIFEST.md)。
  **第一优先是整机爆炸图** `assets/images/exploded-overview.png`——
  团队手上已经有这张渲染，而且首页、What you get、BOM、Assembly 四个页面在等同一个文件。
  然后是 5 张子装配爆炸图（腿/臂/躯干/云台/夹爪）、40 张步骤渲染、6 张走线照片。
  走线照片必须在装配**过程中**拍，事后补不出来。
- **一次装配工时记录**：分阶段的人·小时、几个人同时、哪些步骤要吊具。
  在**第二次**装配时测，不是第一次。

### 三处已知的上游文档矛盾，顺手修掉

1. `control/docs/OPERATIONS.md` T1 说两个 RealSense "sit side by side on the head
   gimbal"，但 `humanoid_gimbal_zero_check.py`、`calibrate_cam_gear.py`、
   SETUP.md 的端口表和项目 README 全都描述的是两个独立云台、一前一后。
   站里跟着工具走并标出了矛盾，上游那句应该改掉。
2. 夹爪舵机 ID：端到端服务写 left=5 / right=0，同一个仓库里的台架脚本对右手用 19。
3. CAD 溯源里相机组件叫 `IntelRealsense_D435_Multibody`，而零件表、README 和
   外参脚本全写 D436。两个型号的安装包络不一样，开机加工之前必须确认。

---

## 8. 维护这个站的几条硬规矩

1. **不许编硬件事实。** 扭矩、线规、螺钉长度、打印温度、间隙——
   没有可核实来源的，进 TODO 块，不进正文。
2. **不许手打价格。** 调宏。也不许在 `bom_total([...])` 里手写文件名列表。
3. **不许给不存在的图写真 `![](…)`。** 整站构建会挂。
4. **每个 TODO 必须有 `*Owner:*`。** 生成器会因此失败退出，这是故意的。
5. **已知缺陷不许粉饰。** `docs/bom/index.md` 那张缺陷表是故意发出去的。
   修好了删行，没修好不许改措辞。
6. **正文英文，TODO 标题是唯一例外**（`TODO — 待填`）。
7. **改完必须跑**：

   ```bash
   python tools/gen_punchlist.py
   python tools/gen_image_manifest.py
   mkdocs build --strict     # 必须 exit 0，且一条 WARNING 都没有
   ```

   CI 跑的就是 `--strict`；它同时就是链接检查器。唯一允许出现的 `INFO` 是
   `data/README.md` 和 `assets/MANIFEST.md` 不在 nav 里——这两个是故意的。
