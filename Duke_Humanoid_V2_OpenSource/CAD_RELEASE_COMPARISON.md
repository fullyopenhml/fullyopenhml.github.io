# 四个开源机器人怎么发布设计文件：对比与 Duke V2 方案

> 调研日期：2026-09-18。对象：OpenArm（Enactic）、Asimov 0/1（Menlo Research）、ToddlerBot 2.0（Stanford）、Berkeley Humanoid Lite（UC Berkeley）。
> 下面关于这四个项目的每条事实都来自调研记录，关键处附了 URL 或本地路径。各项目的完整文件树保存在 `reference/_meta/cad-trees/`。

---

## 1. 一句话结论

四家里没有一家把“买零件、加工、打印、组装”全流程做完整。可以把各家做得最好的一块拼起来用：**OpenArm 让机加工件能按型号直接下单（MEVIY），Asimov 用零件编号同时写明子装配和工艺，并按工艺分目录，ToddlerBot 和 Berkeley 给打印件提供现成的 3MF 打印盘，ToddlerBot 还写了“把 ZIP 上传到这家厂”的逐步下单教程。** Duke 应该把这几样都做上，并把所有文件和 license 放进同一个有版本号的 GitHub 仓库和 Release。另外要注意：OpenArm 只有 2025-07 的 1.0 版用 Fusion 360，之后改用了 SolidWorks 2025，而且它从来没有公开过 `.f3d`/`.f3z`。所以没有现成的“Fusion 360 发布范本”可以照搬。

---

## 2. 对比表

| 项目 | CAD 软件 | 发布了什么格式 | 放在哪 | 机加工件怎么下单 | 打印件怎么给 | 在线 3D 查看 | 套件或成品 | 硬件 License |
|---|---|---|---|---|---|---|---|---|
| **OpenArm** | 1.0 用 Fusion 360（根据 STEP 文件头推断），2025-08 起用 SolidWorks 2025 | 1.0.1：整机 STEP、逐零件 STEP、SLDPRT/SLDASM、STL、3MF、线缆 PDF、Gerber。2.0：手臂只有整机 STEP 和 BOM.xlsx（Cell、KER 另有整机 STEP、BOM 和 PCB 文件） | 先放在 git 里，2025-11 起改为 Google Drive 为“唯一真源”，GitHub Release 做镜像 | **MISUMI MEVIY 型号**：买家把 BOM 里的型号粘贴到 MISUMI 下单 | 1.0 提供 STL 和 Bambu 3MF，2.0 什么都没有 | 没有 CAD 查看器，只有 MuJoCo 网页仿真 | 有认证制度，WowRobo 卖 V2 $6,500，另有 8 家未认证的第三方 | CERN-OHL-S-2.0（只在 GitHub 仓库里有声明） |
| **Asimov 1** | SolidWorks 2025/2026 | 165 个逐零件 STEP、整机 STEP（387 MB）、17 张螺纹图纸 PDF、热熔螺母位置 PDF、KiCad 工程 | 一个 GitHub 单仓库（整机 STEP 放在 LFS），查看器放在自建 CDN | 没有渠道，只有 STEP 和按工艺分的目录 | 只有 STEP（MJF/SLM），没有 STL 或 3MF | eDrawings HTML，以及自研的 Origami 装配播放器（GLB） | DIY 套件 $20,000 | CERN-OHL-S-2.0 |
| **ToddlerBot 2.0** | Onshape | Onshape 在线文档（匿名用户不能导出）、MakerWorld 3MF、只能用于仿真的 STL、PCB Gerber | Onshape、MakerWorld、GitHub、Google Sheet | 没有机加工件，全部打印。PCB 有 JLCPCB 逐步下单教程 | MakerWorld 3MF，19 个打印盘，每盘写明材料、克数、打印时间 | Onshape 匿名查看、tnkr.ai 上的 GLB | WowRobo 成品 $4,299（项目声明与其无关） | CC BY-NC-SA 4.0（写在 README 和 MakerWorld 页面；仓库的 LICENSE 文件是 MIT，只管代码和文档） |
| **Berkeley Humanoid Lite** | Onshape | Onshape 在线文档（允许匿名导出）、MakerWorld 3MF 和 STL、只能用于仿真的 URDF/MJCF/USD | Onshape、MakerWorld、Google Sheet、GitBook，GitHub 上只有仿真文件 | 没有机加工件，全部打印，金属件都是现成品 | MakerWorld 3MF（整机 9 个盘），执行器另附 STL | Onshape 匿名查看 | 没有 | 混乱：GitHub 是 CC BY-SA，MakerWorld 是 CC BY，CAD 没写 |

---

## 3. 让“有钱就能造出来”的三条路

### 3.1 机加工件直接按号下单

**谁做到了：只有 OpenArm。**（`reference/openarm/md/1.0/hardware/bill-of-materials/procuring-components.md`）

- **机制**：1.0 手臂的 27 种定制件、1 种底座板、4 种夹爪件，全部预先在 MISUMI MEVIY 登记了型号。例如 J1_A = `MVBLK-ASN-48S-4BGUX-L`，数量 2，单价 ￥7,222。设计方在 MEVIY 里选择「どなたでも購入可能な型番を発行」（任何人都能购买），这是默认设置。另外还可以设置「海外における購入権限」，限定哪些国家/地区能买。（https://jp.meviy.misumi-ec.com/help/ja/operation_manual/others/2754/ ）
- **买家怎么操作**：登录 MISUMI 账号，打开 https://jp.misumi-ec.com/order/part-number/create ，粘贴 BOM 里的型号，系统会识别为 MEVIY 定制件，填好数量就能下单，不用上传 CAD。文档原话是「ensures you get the exact geometry we've validated」。如果想走别的路，也可以自己把 STEP 上传到 meviy.misumi-ec.com 报价（方法 1）。
- **代价和问题**：
  - 零件是按 MEVIY 的工艺能力设计的。issue #15 指出 J2_A、J8_B 有 MEVIY 能做、普通 CNC 做不了的特征，至今 open。
  - issue #12 有人抱怨定制件只给 MEVIY 型号、拿不到 CAD，至今 open，无回复。
  - 1.0 只给 STEP，没有 2D 图纸和公差。钣金件没有展开图（issue #13 问过，已关闭，看不到回复）。
  - 日本以外能不能买、型号现在是否还有效，都**没有核实**（见第 6 节）。
- **对照组**：Asimov 有 43 个 7075 铝件和 18 个 316L 件，但没有任何下单渠道，唯一的工艺说明是 “A 件 should be CNC machined”。Asimov 的 PCB 反而做得更好：KiCad 源文件里带 LCSC 料号，可以直接交给 JLCPCB 生产。
- **Duke 要做到同样程度需要**：
  1. 每个机加工件有独立 STEP，另外至少有一张 PDF 图纸，写明螺纹、关键公差、材料和表面处理。OpenArm 和 Asimov 都没提供公差，这正是买家拿去找别的厂报价时缺的东西。
  2. 如果选定一家支持“设计方登记零件、别人按号购买”的加工服务，就把每个零件的服务型号写进 BOM 的一列。能在美国做到 MEVIY 这种效果的服务，这次**没有调研**，需要团队自己确认。
  3. 就算没有这种服务，也可以照 ToddlerBot 的 JLCPCB 教程写一页：“把 `machined/` 目录打成 ZIP → 上传到某厂 → 选这个材料和表面处理 → 下单”，每一步配截图。

### 3.2 打印件一键打印

**谁做到了：ToddlerBot 和 Berkeley 做得最完整，OpenArm 1.0 做了一部分。**

- **ToddlerBot**（https://makerworld.com/en/models/1733983 ）：在 MakerWorld 上每个型号发一个 Bambu Studio 3MF 打印配置，名称是 “0.2mm layer, 6 walls, 25% infill”，面向 X1 Carbon、0.4 mm 喷嘴。2XC 一共 19 个打印盘（前 18 个有名称，第 19 个没命名）（Arm、Leg_L、Torso、Waist、Safety Stand、SysID……），合计约 83.6 h、2437 g。每个盘写明耗材种类、颜色、克数和时间，例如 Torso 10.0 h / 312 g PLA-CF。买家点 “Open in Bambu Studio” 就能开始打印，零件朝向和支撑都已经摆好。不用 Bambu 打印机的人，文档让他们打开 3MF 看朝向。
- **Berkeley**（https://makerworld.com/en/models/1327260-berkeley-humanoid-lite ）：
  - 执行器按打印参数分成两个配置：Housing 用 4 圈墙、15% 填充；Shaft 用 5 圈墙、80% 填充。
  - 整机有 9 个打印盘，合计 1004 g、约 28.8 h。
  - GitBook 页面放了 Bambu Studio 各设置标签页的截图。
  - 问题一：3MF 里只有一侧的零件，另一侧要用户自己在切片软件里镜像。
  - 问题二：配置标题写 “5 walls, 80%”，但读到的全局参数是 2 圈墙 / 15%，两者冲突，原因未核实。
- **OpenArm 1.0**：`STL/covers/left/left_covers.3mf` 带完整切片参数，包括 Bambu Studio 02.02.01.58、X1C、PLA、100% 填充、6 圈墙、tree 支撑、220/55 °C。但文档里没写这些参数，到了 Drive v1 只剩 STL，2.0 连 STL 都没有了。
- **Asimov**：打印件只给 STEP，并规定必须用 MJF PA12 或 SLM 316L，原话是 FDM “will not guarantee the tolerances and required strength”。也就是说打印交给服务商，项目不提供切片文件。
- **Duke 要做到同样程度需要**：
  1. 给打印件出一个或几个 3MF 项目，按子装配命名打印盘，并在 README 里用文字写一份参数表，包括材料、层高、墙数、填充、支撑。只存在 3MF 里的参数，别的切片软件用户看不到。
  2. 左右件两侧都放进 3MF，不要让用户自己镜像。
  3. 同时发裸 STL，方便非 Bambu 用户。
  4. 可以选择再发到 MakerWorld，但 license 必须和仓库一致（Berkeley 就是反例）。

### 3.3 买套件或成品

| 项目 | 渠道 | 价格和条件 | 项目本身的态度 |
|---|---|---|---|
| OpenArm | docs.openarm.dev/purchase/：Official Manufacturing Partners 加 All Manufacturers 两层，外加认证 | WowRobo “Certified ★★★”：V2 $6,500、V1.1 $5,400、KER $2,599，交期 20–40 天，全球发货。另有 VLAI、Cereboto、Soma、Anvil、PowerZ、SVTRobotics、Tianjin Muniu Liuma、MJTWO 共 8 家（“Evaluating...” 或 “Not evaluated”），标价在 $4,699（VLAI）到 $7,080（Cereboto 带相机版）之间，Soma 以人民币标价 CNY 45,800（页面折合 $6,430）。厂商发邮件到 openarm@enactic.ai 申请上榜 | 最制度化。页面附有 Discord 评价频道和举报虚假宣传的邮箱。但同一页里 RT Corporation 既被列为 Official Partner，表格里又标着 “Evaluating...”，自相矛盾 |
| Asimov | https://menlo.ai/order | DIY Kit $20,000，定金 $499，发货 30–60 天，保修 90 天，不接受退货。整机要找销售询价 | 自己卖套件。另有供应链合作伙伴计划（https://docs.menlo.ai/partners），原话是 “Similar to LeRobot and OpenArm” |
| ToddlerBot | WowRobo 成品 $4,299（https://shop.wowrobo.com/products/toddlerbot-2-0-assembly-version ），不含 Jetson、WiFi、电池 | 30 天预售 | 放在 BOM 表第一行，下一行就是免责声明，说明项目与其无关、未测试。但 WowRobo 自称 “Official Recommended Purchase Channel”，两边冲突。而且项目 license 带 NC（禁止商用），WowRobo 是否另获许可不清楚 |
| Berkeley | 没有 | — | 纯 DIY。BOM 里每个零件都给了美国（Amazon/Digikey）和中国（Taobao/Tmall）两套采购链接 |

**Duke 要做到同样程度需要**：先定 license，再决定要不要设合作厂商名单。如果选 CERN-OHL-S，商业厂商可以合法生产（OpenArm、Asimov 就是这种情况）。如果选 CC BY-NC-SA，厂商卖成品就会落在许可范围之外（ToddlerBot 的情况）。上榜名单这件事可以晚一点做，但文档里应当先留一页 “Buying Duke V2”，写明认证的标准。

---

## 4. 每个项目的做法细节

### 4.1 OpenArm（Enactic）

- 仓库：https://github.com/enactic/openarm_hardware （tag 1.0.0 / 1.0.1 / 1.1.0 / 2.0.0）。文档站：docs.openarm.dev。
- **软件**：1.0 的 STEP 文件头是 `Autodesk Translation Framework v14.10.0.0` 和 `ST-DEVELOPER v20.1`，STL 文件头是 `STLB ATF 14.10.0.0`，这是 Fusion 导出器的签名。2025-08-22 的 commit e20a47b “added SolidWorks files” 之后，文件头变成 `SwSTEP 2.0` / SolidWorks 2025。README 里 “Fusion 360 assemblies” 这句话已经过时（`reference/openarm/repo/README.md`）。48 个 commit 的完整历史里从没出现过 `.f3d` 或 `.f3z`。
- **托管的演变**：
  1. 最初直接提交在 git 里，没用 LFS，29 MB 的 STEP 也直接提交。
  2. 2025-11-13 的 commit e0f3e69 删除了 184 个文件，改为 “Google Drive is the source of truth”。
  3. 之后的发布流程：`dev/google-drive-files/generate-file-ids.rb` 生成 `file-ids.tsv`；`.github/workflows/release.yaml` 从 Drive 下载文件，打成 `openarm-hardware-<版本>.tar.gz`，附上 sha256/sha512 校验和，再发布到 Release。1.1.0 的包有 249 MB。
- **1.0.1 的目录（节选）**：
```
STEP/OpenArm01_follower.step  OpenArm01_leader.step
STL/covers/left/j1-a-left.STL … left_covers.3mf
STL/leader/rail-connector-leader.STL swivel-link-leader.STL …
SolidWorks/SLDPRT_Files/J1_A.SLDPRT … J8_B.SLDPRT
SolidWorks/STEP_Files/J1_A.STEP …          (与 SLDPRT 同名)
SolidWorks/assemblies/OpenArm01_{follower,leader}_{bimanual,left,right}.SLDASM
SolidWorks/motors/DM-J4310-2EC.SLDPRT …
SolidWorks/off-the-shelf/CBE3-6.SLDPRT …   (文件名就是 MISUMI 型号)
Electrical/J1_J2.pdf … Gerber_For_Hub.zip BOM_For_Hub.csv CPL_For_Hub.xlsx
```
- **命名**：结构件按关节加字母命名（J1_A…J8_B），左右件带 `_left`/`_right`，打印件用 kebab-case。命名有不少不一致：扩展名 `.STL` 和 `.stl` 混用；同一零件在 SLDPRT 里叫 `left_jaw`，在 STL 里叫 `left-jaw`；`left-pincer.STL` 的文件头内部名写的是 `right_pincer_v2`。
- **BOM**：1.0 的 BOM 是手写在 TypeScript 数组里的（`website/src/components/ArmOffTheShelfTable.tsx`）。BOM 的名字和 `SolidWorks/STEP_Files/J1_A.STEP` 同名。紧固件直接写 MISUMI 型号，例如 CBE3-6 ×146，单价 ￥44。2.0 的 BOM.xlsx 没有价格，有些行直接写了未公开的 `.SLDPRT` 文件名。
- **外购件**：2.0 README 说外购件只放简化模型，是为了遵守零件厂商的 CAD 许可。
- **仿真文件**：放在另外两个仓库 enactic/openarm_description（URDF）和 enactic/openarm_mujoco（MJCF），都是 Apache-2.0。
- **可以照抄**：每个机加工件都登记成任何人可购买的服务型号，写进 BOM，同时公开逐零件 STEP，给想找别家加工的人用。
- **不要学**：把 CAD 从有版本的 git 搬到可以随意改动的 Drive，最后只剩一个 48 MB 的整机 STEP。Drive 上没有 LICENSE 文件，1.0 文档仍然指向已经空了的仓库，而且 Release 发布一周多就和 Drive 对不上了（`KER_CABLE_TOPO.png` 等文件已从 Drive 消失）。

### 4.2 Asimov 0 / 1（Menlo Research）

- 仓库：https://github.com/menloresearch/asimov-1 和 https://github.com/menloresearch/asimov-v0 （原 asimovinc 组织的地址会 301 跳转过来）。文档：https://docs.menlo.ai 。
- **软件**：165 个 STEP 的文件头都是 `SolidWorks 2025`，图纸 PDF 由 SOLIDWORKS 2025 SP3.0 / 2026 SP1.1 生成。原生文件没有公开。PCB 用 KiCad，头部板用 EasyEDA Pro。
- **目录（节选，完整清单见 `reference/_meta/cad-trees/asimov-asimov-1.txt`）**：
```
HARDWARE-LICENSE.txt  SOFTWARE-LICENSE.txt
scripts/generate_fabrication_manifest.py
.github/workflows/fabrication-manifest.yml
mechanical/naming_convention.png
mechanical/ASV1/
  FullBodyAssembly/Asimov_1.STEP                 (LFS, 387 MB)
  100/FABRICATION/ALU_7075/ASV1_100_02A.STEP
  100/FABRICATION/MJF_PA12/ASV1_100_01C.STEP
  100/FABRICATION/OFF_THE_SHELF/ASV1_100_15X.STEP
  200/FABRICATION/SML_316L/ASV1_200_04B.STEP
  ...（100–700 各子装配结构相同）
  Docs/Drawing_thread_parts/*.pdf  Docs/Heat_Insert_parts/*.pdf
electrical/wiring/motor-wires.csv  misc-wires.csv
sim-model/urdf/asimov_1.urdf  sim-model/xmls/asimov_1.xml
```
- **命名**：格式为 `ASV1_<子装配码>_<两位序号><工艺字母>`。
  - 子装配码：100 躯干、200 腰、300/350 右臂/右手、400/450 左臂/左手、500/600 右腿/左腿、700 头。
  - 工艺字母：A = CNC 7075，B = SLM 316L，C = MJF PA12，X = 外购件。
  - 不一致的地方：目录名写成 `SML_316L`（工艺是 SLM）；`ASV1_500_23A_SS` 放在 ALU 目录里，图纸上写的却是不锈钢；STEP 文件内部的 FILE_NAME 和外部文件名对不上。
- **LFS**：`.gitattributes` 写了 `*.STEP filter=lfs`，但 165 个单件 STEP 实际是普通 blob，只有整机 STEP 真正在 LFS 里。两个仓库都没有 GitHub Release。
- **图纸**：只有 17 个带螺纹的零件有 PDF 图纸，图上有螺纹标注和材料，但没有公差、表面处理和标题栏。
- **紧固件**：GitHub 上的 STEP 里一颗螺钉都没有。但 Origami 播放器的 `project.json` 显示内部装配里建了紧固件，例如 158 个 M4 热熔螺母、141 个 M3×12。只是没有导出成清单。
- **BOM**：锁在 Tally 表单后面（https://tally.so/r/jaG0va ），要填邮箱。README 指向的 `mechanical/FABRICATION_MANIFEST.csv` 是 404。
- **3D 查看器**：
  - eDrawings HTML：57 MB 和 124 MB 的单文件，模型以 base64 内联。这是 SolidWorks 专有的导出格式。
  - Origami 播放器：基于 three.js，加载 201 个 Draco 压缩的 GLB，合计 8 MB。可以用 `?step=`、`?part=` 参数跳到某一步或某个零件，每个装配步骤都嵌了一个 iframe。播放器本身没有开源。
- **可以照抄**：用机器可读的零件编号同时写明子装配、序号和工艺，并按 `<子装配>/FABRICATION/<工艺_材料>/` 存放，这样买家可以把一个文件夹整个发给一类供应商。再配一个脚本加 CI，从目录树自动生成清单。
- **不要学**：把 BOM 锁在留邮箱的表单后面，以及链接到根本不存在的清单或 BOM 页。

### 4.3 ToddlerBot 2.0（Stanford）

- 仓库：https://github.com/hshi74/toddlerbot （单仓库，没有硬件专用仓库，没有 LFS，没有 Release，只有 tag v1.0.0 / v2.0.0）。
- **软件**：机械用 Onshape，PCB 用 KiCad 7.0.7。主文档 https://cad.onshape.com/documents/565bc33af293a651f66e88d2 是公开的，但 `anonymousAllowsExport=false`，匿名用户能看不能导出。腿、臂和外购件库放在链接的其他文档里，匿名访问都是 403。
- **仓库目录（节选）**：
```
toddlerbot/descriptions/
  onshape_to_robot.py
  assemblies/2xc_430_palm/ left_leg_2xc_430/ left_arm_gripper/ …
      config.json robot.xml assets/merged/<link>_visual.stl
  toddlerbot_2xc/toddlerbot_2xc.urdf toddlerbot_2xc.xml …
docs/_static/TTLPowerBoardV8.zip bom_v8.csv positions_v8.csv assembly_manual.pdf
```
  仓库里 605 个 STL（872 MB）都是仿真网格，不是打印文件。
- **命名**：Part Studio 用 PascalCase，零件和装配用 snake_case，而且直接就是 URDF 的 link 名。机型变体用 Onshape 的 configuration 实现（2xc/2xm、palm/gripper），不单独存文件。
- **BOM**：Google Sheet，99 行，只列外购件，不列打印件。紧固件是按套装买的。Sheet 和 Onshape BOM 名字、数量都对不上，例如 Sheet 写 AXK0414 ×30，Onshape 是 ×18。精确到每一步的螺钉用量只写在 v1.0 的 `assembly_manual.pdf` 里，而这份手册还没更新到 2.0。
- **PCB 下单教程**：文档 02_pcb8ch 这一页写了在 JLCPCB 下单的每一步：上传 Gerber ZIP → 选 PCBA → 上传 BOM 和 CPL → 缺货时换成指定的替代料号。每一步都配截图。
- **可以照抄**：每个型号一个现成的切片项目，打印盘命名清楚，每盘标明材料、克数、时间；再配一份逐步点击的“把这个 ZIP 上传到这家厂”教程。
- **不要学**：让一个没有版本、需要登录、匿名不能导出的在线 CAD 成为几何的唯一来源。MakerWorld 上有用户因为注册不了 Onshape，公开询问还能从哪里拿到 CAD（**未核实**：复核时 MakerWorld 评论接口里没搜到这条）。

### 4.4 Berkeley Humanoid Lite（UC Berkeley）

- 硬件文件分散在四处：4 个公开 Onshape 文档、3 个 MakerWorld 模型、Google Sheet BOM、GitBook 文档站（https://berkeley-humanoid-lite.gitbook.io/docs/releases ）。GitHub 上只有软件和仿真资产。
- **Onshape**：整机文档 `fc6443b1d89dcba950e85b60` 允许匿名查看，且 `anonymousAllowsExport=true`，但链接指向会继续变动的 Main workspace（`w/`），不是冻结版本（`v/`）。
- **Onshape 标签页组织**：22 个子装配按关节命名，和 URDF link 名完全一致（例如 `leg_left_hip_pitch`）。Part Studio 按“模块 + 部位 + 打印机变体”命名，例如 “6512 Housing Knee - Bambu”。STL 用 Onshape 默认的导出名 `<Part Studio> - <Part>.stl`。
- **GitHub 仿真资产**：
```
Berkeley-Humanoid-Lite-Assets/data/robots/berkeley_humanoid/berkeley_humanoid_lite/
  urdf/  mjcf/  meshes/<link>_visual.stl ×26  scad/ ×8  usd/ (62 MB，未用 LFS)
```
  由 onshape-to-robot 生成，Release 的 zip 由 CI 打包。
- **机加工件**：没有，是有意为之，所有零件都能放进 200 × 200 × 200 mm 的打印空间。打印机之间的公差差异，是靠另建 “- Bambu” / “- Ender” 两套 Part Studio 解决的。
- **BOM**：Sheet 分 3 个标签页，没有料号，没有打印件。整机层面的紧固件只有一行 “Misc Fasteners $40”。Onshape 的 BOM 里 Part number 全部为空，材料还标错了（打印件标成 “Alumina Oxide”）。2025-05-29 补上漏掉的 6803 轴承和 M2 热熔螺母（Release Log 原文 “M2 insert”），起因是用户在 MakerWorld 评论区报告缺件。
- **可以照抄**：一个统一的 Releases 页，每个模块一行，分别链接 CAD、3MF 和 BOM，再配一份带日期的硬件修订日志。CAD 子装配直接按 URDF link 命名，这样仿真模型能从同一份 CAD 自动导出。
- **不要学**：几个平台上的文件都不带版本，license 还各不相同（GitHub 是 CC BY-SA，MakerWorld 是 CC BY，CAD 没写 license）。MakerWorld 的文件还和 CAD 不一致过（6512 最初上传的是 5010 的几何）；整机打印配置还被 MakerWorld 下架过一次（设计者称因缺实拍图），文档里指向旧配置 `#profileId-1364871` 的链接因此失效。

---

## 5. 给 Duke V2 的具体方案（Fusion 360）

### 5.1 以谁为模板

- **没有能直接照搬的 Fusion 范本。** OpenArm 只有 1.0 用 Fusion（从 STEP 文件头推断，文档也这么写），它当时发的也不是 Fusion 原生文件，而是 Fusion 导出的整机 STEP 和 STL；逐零件 STEP 和 SLDPRT/SLDASM 是 2025-08 用 SolidWorks 加的，3MF 是 2025-08-27 用 Bambu Studio 加的。2025-08 以后 OpenArm 改用了 SolidWorks。所以从 OpenArm 能借鉴的是它的发布方式和 MEVIY 下单流程，这些都和用什么 CAD 软件无关。
- **建议组合**：
  - 目录和命名学 Asimov：按子装配分，再按工艺和材料分，零件编号里带工艺字母。
  - 机加工件下单学 OpenArm：给每个零件一个服务型号，同时公开逐零件 STEP。
  - 打印件学 ToddlerBot：3MF 打印盘，每盘写明材料、克数、时间。
  - 外购件和 PCB 学 ToddlerBot 的 JLCPCB 教程，以及 OpenArm 的“型号直接写进 BOM”。
  - 版本和托管学 OpenArm 早期（1.0.1）：所有文件都在 git 里，用 tag 打版本，Release 附带 tar.gz 和校验和。**不要**学它后来搬到 Drive 的做法。
- **license**：CERN-OHL-S 要求提供修改时首选的原始形式（“Source”）。Asimov 选了 CERN-OHL-S 却只发了 STEP，这一点有问题。Duke 如果也选 CERN-OHL-S，就应该发布 `.f3z`，这样才真正满足它的要求。LICENSE 文件要放在仓库根目录，**并且**打进每个 Release 包（OpenArm 的 Drive 里没有 license，这是反例）。

### 5.2 目录和命名

```
duke-humanoid-v2-hardware/
├── LICENSE-HARDWARE.txt          (例如 CERN-OHL-S-2.0，由团队和导师决定)
├── README.md                     (版本、快速入口：CAD / BOM / 打印 / 下单 / 组装)
├── CHANGELOG.md                  (带日期的硬件修订日志)
├── bom/
│   ├── DV2_BOM.csv               (唯一 BOM，含紧固件，带版本号，和 CAD 放在一起)
│   └── DV2_fasteners.csv         (可选：紧固件汇总，按规格和数量列出)
├── cad/
│   ├── native/DV2_FullRobot_v2.0.f3z        (Fusion 原生归档)
│   ├── assembly/DV2_FullRobot_v2.0.step     (整机 STEP)
│   └── parts/
│       ├── 100_torso/
│       │   ├── machined_AL6061/DV2_100_01A.step  DV2_100_01A.pdf
│       │   ├── printed_PLA/DV2_100_05C.step  DV2_100_05C.stl
│       │   └── purchased/        (只放外形或简化模型，受厂商许可限制时不放)
│       ├── 300_right_arm/ …
│       └── 500_right_leg/ …
├── print/
│   ├── DV2_print_all_v2.0.3mf    (命名打印盘，左右件都有)
│   └── PRINT_SETTINGS.md         (材料、层高、墙数、填充、支撑的文字版)
├── machining/
│   └── HOW_TO_ORDER.md           (逐步上传、选材料、选表面处理的教程，配截图)
├── electrical/                   (原理图 PDF、Gerber、JLCPCB 格式的 BOM 和 CPL、线束表 CSV)
├── assembly/                     (组装手册 PDF，每一步列出紧固件规格和数量)
└── scripts/make_manifest.py      (扫描 cad/parts 自动生成零件清单，CI 检查是否最新)
```

**命名规则**：`DV2_<子装配码>_<两位序号><工艺字母>`。
- 子装配码可以直接借用 Asimov 的分段方式（100 躯干 … 700 头），但要按 Duke 的 31 DoF 结构自己定。
- 工艺字母例如 A = CNC 铝、S = 钣金、C = 打印、X = 外购件，这一套字母也由团队自己定。
- 同一套编号要**在 Fusion 里作为组件名**使用，这样导出的 STEP、STL、图纸和 BOM 自然同名。Asimov 出现过 STEP 内部名和外部文件名对不上的问题，就是因为编号没有和源文件同步。
- 扩展名统一小写。OpenArm 和 Asimov 都出现过大小写混用。
- 左右件用两个编号，两侧的文件都要发，不要让用户自己镜像。
- 如果仿真 URDF 从同一份 CAD 导出，子装配名最好和 URDF link 名对应（Berkeley 的做法）。

### 5.3 每类零件发布什么格式

| 零件类别 | 发布内容 | 理由 |
|---|---|---|
| 机加工件（CNC / 钣金） | 逐零件 STEP，外加 PDF 图纸（螺纹、关键公差、材料、表面处理）。钣金件加 DXF 展开图 | 四家都没给公差。OpenArm 被问过展开图（issue #13）；Asimov 的图纸只标了螺纹 |
| 打印件 | 逐零件 STEP 和 STL、3MF 打印项目，再加一份文字版参数表 | ToddlerBot 和 Berkeley 的做法。参数只存在 3MF 里是 OpenArm 的教训 |
| 外购件（电机、轴承、螺钉） | 不发几何，或只发简化外形；BOM 写厂商料号和采购链接 | OpenArm 2.0 README 为了遵守厂商 CAD 许可只放简化模型。OpenArm 1.0 把 MISUMI 型号直接写进 BOM 和文件名，买家可以照着搜索下单 |
| 整机 | 整机 STEP 和 `.f3z` | 整机 STEP 方便看整体，`.f3z` 是 CERN-OHL-S 要求的原始形式 |

**要不要发 `.f3z`/`.f3d`**：建议**发 `.f3z`**。四家里只有 OpenArm 1.0.1 曾在 git 里放过 SolidWorks 原生文件（1.1 起删除），Asimov 只发 STEP，ToddlerBot 和 Berkeley 只有在线 Onshape 文档、没有可下载的原生文件，结果 Berkeley 被评论区索要 STEP 和 SolidWorks 文件，OpenArm 的 issue #12 抱怨拿不到 CAD，ToddlerBot 据称有用户因为注册不了 Onshape 拿不到 CAD（**未核实**）。原生文件加逐零件 STEP，能覆盖所有需求。

### 5.4 托管

| 内容 | 放在哪 | 理由 |
|---|---|---|
| 逐零件 STEP、STL、PDF、BOM CSV、3MF、文档 | GitHub 仓库，用 git tag 打版本 | OpenArm 1.0.1 在 git 里时最全，搬到 Drive 后就乱了 |
| 大文件（整机 STEP、`.f3z`） | Git LFS **或者** GitHub Release 附件（二选一，并确认 `.gitattributes` 真的生效） | Asimov 387 MB 的整机 STEP 在 LFS 里，但 `.gitattributes` 写了规则的单件 STEP 实际没进 LFS |
| 发布包 | GitHub Release：`duke-v2-hardware-<版本>.tar.gz`，附 sha256，包里含 LICENSE | 照 OpenArm 的 `release.yaml` 思路，但数据源是 git 仓库本身，而不是 Drive |
| 在线 3D 查看 | Fusion 公开分享链接（**必须是冻结的版本**），或导出 GLB 用 three.js 自己做 | ToddlerBot 和 Berkeley 都链接到会变动的 workspace。Asimov 的 eDrawings 是 SolidWorks 专有格式，Fusion 做不出来。Fusion 分享链接能否匿名查看和导出，这次**没有实测** |
| 3MF | 以仓库为准，可以再镜像到 MakerWorld | 镜像要写同一个 license、同一个版本号（Berkeley 两边的 license 不一致）|
| 不要用 | Google Drive 做“唯一真源”；留邮箱才能下载的表单 | OpenArm 的 Drive 和 Release 对不上；Asimov 的 BOM 锁在表单后面 |

### 5.5 机加工件能下单，打印件一键打印

- **机加工件**：
  1. 最低要求是 `machining/HOW_TO_ORDER.md`：把某个 `machined_*` 目录打成 ZIP，上传到某厂，选定材料、表面处理和数量，每一步配截图（照 ToddlerBot 的 JLCPCB 教程写）。
  2. 更进一步是 OpenArm 的做法：在支持“公开型号”的服务上登记每个零件，把型号写进 BOM 的 `order_code` 列。MEVIY 能否从日本以外购买，这次**没核实**；美国有没有等价的服务，这次**没调研**。
  3. 设计时注意不要依赖某一家的独有工艺。OpenArm 的 J2_A、J8_B 普通 CNC 做不了，就是反例。
- **打印件**：
  1. 3MF 按子装配分打印盘，左右件都有。
  2. 盘名写明材料、克数、时间，例如 `Leg_R – PLA-CF – 312 g – 10 h`。
  3. `PRINT_SETTINGS.md` 用文字写一遍参数。
  4. 3MF 标题和实际参数要一致（Berkeley 的标题和全局参数是冲突的）。

### 5.6 BOM 怎么和 CAD 文件名对应

- 每个自制件在 BOM 里占一行，`part_id` 一列和文件名完全相同（例如 `DV2_500_02A`）。OpenArm 1.0 的 J1_A 做到了这一点，1.1 以后逐零件 STEP 被删，BOM 就对不上任何文件了。
- 建议的列：`part_id, name, subassembly, process, material, finish, qty, file_step, file_drawing, order_code, supplier, supplier_pn, unit_price_usd, notes`。
- 紧固件和轴承也要逐行写：规格、DIN/ISO 标准号、数量、供应商料号。反例是 Berkeley 的 “Misc Fasteners $40” 和 Asimov 那种没有标准号的通用名称。
- 用 `scripts/make_manifest.py` 从 `cad/parts/` 目录树生成清单，再在 CI 里核对 BOM 中每个自制件都有对应文件，反过来也一样。这是 Asimov 的思路，但生成出来的文件一定要提交，他们的 `FABRICATION_MANIFEST.csv` 因为没提交而是 404。
- 如果能从 Fusion 导出 BOM，就拿它来校对手写 BOM 的数量。四家的 BOM 全是手写的，都出现过数量不一致或漏件。Fusion 的 BOM 导出功能这次**没有实测**。

### 5.7 现在让团队交的东西够不够

目前让团队往 `/Users/rivery/Desktop/DukeV2OpenSource/cad/` 交两样（2026-09-18 该目录还是空的）：(a) 一个整机 STEP，(b) 原生 `.f3z`。这两样**都要，但不够**。只交这两样，结果会接近 OpenArm 2.0，也就是只有一个整机文件，买家得自己从里面拆零件。建议补充以下几项：

1. **导出前先改组件名**：在 Fusion 里把每个自制件的组件名改成 `DV2_<子装配>_<序号><工艺>`。这一步最重要，后面所有文件名都依赖它。
2. **逐零件 STEP**：每个自制件一个，放进 `cad/parts/<子装配>/<工艺_材料>/`。
3. **打印件的 STL**：再加一个排好盘的 3MF，以及打印参数（材料、层高、墙数、填充）。
4. **机加工件的 PDF 图纸**：至少写螺纹、关键配合公差、材料、表面处理。钣金件另给 DXF 展开图。
5. **一份 BOM CSV**：自制件、外购件、紧固件全部逐行列出，`part_id` 和文件名一致。
6. **版本号**：`.f3z` 和整机 STEP 的文件名里写版本（例如 `_v2.0`）。Fusion 里对应的版本号记录在 CHANGELOG 里。
7. **可选**：如果要用 Fusion 公开链接做在线查看，链接必须指向冻结版本；也可以导出 GLB，自己做查看页。
8. **外购件模型**：先确认厂商的 CAD 许可是否允许再分发，不允许的就像 OpenArm 2.0 那样换成简化外形。

---

## 6. 还没核实的地方

**OpenArm**
- 1.0 到底是 Fusion 360 还是别的 Autodesk 产品：文件头特征和文档都指向 Fusion，但从来没有 `.f3d`/`.f3z` 可以直接证实。
- 1.0.1 里的 SLDPRT/SLDASM 是带参数化特征树的原生文件，还是导入 STEP 后的死实体：没下载，无法判断。
- v2 整机 STEP 里的零件名能否和 v2 BOM 里的 `*.SLDPRT` 名字一一对应：要下载 48 MB 的文件才能核对，没做。
- MEVIY 型号能否在日本以外购买（「海外における購入権限」是设计方的私有设置，外面看不到），以及型号现在是否还有效：MISUMI 搜索页返回 403，MEVIY 公开搜索 `MVBLK-ASN-48S-4BGUX-L` 没有结果。
- MEVIY 型号各段的含义（-L / -E 后缀、ASN/SUB/48S/4H8 等字段）：没找到官方解释。
- MEVIY 现价：文档里的日元价格是 1.0 时期的，v2 BOM 不带价格。
- 只读了 `left_covers.3mf` 的切片设置，没读 `right_covers.3mf`。
- 各 Release tar.gz 的内容：没下载，只看了大小和生成它们的 workflow。
- Drive 自带的 STEP 在线预览能不能用：没测。JIG BOM（3.8 MB）没打开。
- issue #13 为什么被关闭：页面上看不到维护者回复。
- openarm.dev 首页的参数数字（DOF、臂展、BOM 成本 $9,000 等）是滚动时才计数的动画，抓到的可能是中间值，不可引用。
- 同一页面上 RT Corporation 既是 Official Partner，表格里又标 “Evaluating...”，官方页面自相矛盾。

**Asimov**
- BOM 电子表格的内容（数量、供应商、价格、有没有紧固件）：锁在 Tally 表单后面，没有提交。
- Origami 每一步的指令 JSON 不在镜像里，不知道每一步用到哪些紧固件。
- 仓库历史：asimov-1 共 29 个 commit，但本次没有逐个翻历史，所以没弄清单件 STEP 为什么绕过了 LFS 规则，也不知道零件编号什么时候改过。
- 组装整机的价格，以及美国和新加坡装配合作伙伴的名字：均未公开。
- Encos 折扣的力度：只公开了折扣码。
- eDrawings HTML 是从 SOLIDWORKS 直接导出的还是用 eDrawings Professional 导出的。
- Fusion 360 能不能做出同等效果的查看器：没实测。
- STEP 文件除文件头以外的内容：没读。

**ToddlerBot**
- MakerWorld 3MF 的内部内容（按对象的参数覆盖、支撑、实际朝向）：下载需要登录，没下载，参数只来自 API 元数据。
- “Download STL/CAD Files” 的 zip 里有什么，有没有 STEP。
- 登录的 Onshape 用户能不能导出 STEP 或复制文档（`numberOfTimesCopied=59` 暗示可以复制，但没测）。
- 那几个返回 403 的 Onshape 文档（sysID、标定治具、安全架、腿、臂、外购件库、V1），对登录用户是否可见。
- Onshape 版本历史：接口返回 401，`recentVersion=null`。
- 通用的 M2–M4 螺钉是否在 Onshape 里建了模、只是没进 BOM（CHANGELOG 说质量分布 “including fasteners”）。
- docs.tnkr.ai 打不开；tnkr.ai 登录用户能否下载 GLB 背后的 STEP。
- `assembly_manual.pdf` 的图片：只提取了文字。
- WowRobo 套件的内容、质量，以及在 NC 许可下有没有和作者另签授权。

**Berkeley Humanoid Lite**
- 3MF 内部内容：整机配置标题 “5 walls, 80% infill” 和全局参数 “2 walls / 15%” 的冲突无法解释。
- Onshape 版本历史：匿名访问返回 401，不确定有没有和 2025-09-07 发布对应的冻结版本。
- 6512 装配的配置选项 “Without-F-M” 是什么意思。
- 匿名用户能否真的从 Onshape 导出 STEP/STL：标志位是 true，但没实际跑导出。
- MakerWorld 页面自带的 3D 预览控件：没截到图。
- 是否有第三方（例如 Taobao）卖套件或打印件：搜不到，但不能证明不存在。
- Google Sheet 的编辑历史。
- MakerWorld 上 5010 的 raw STL 是否包含 2025-08-23 的修正（时间戳仍是 2025-04-16）。

**与 Duke 方案相关、本次调研没覆盖的**
- Fusion 360 公开分享链接能否匿名查看和导出、能否固定到某个版本、BOM 导出和 3MF 导出的效果：都没实测，需要团队在 Fusion 里自己试。
- 美国有没有类似 MEVIY、支持“设计方登记、任何人按号购买”的加工服务：没调研。
