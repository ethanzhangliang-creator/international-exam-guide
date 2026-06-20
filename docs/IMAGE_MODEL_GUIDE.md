# Image Model Guide / 生图模型建议

## English

The guide generator should not depend on image generation for its core factual
output. The current MVP uses deterministic SVG concept maps because they are
easy to trace back to syllabus points.

For many subjects, richer illustrations are still useful:

- science lab apparatus and safety layouts;
- maths geometry diagrams and step-by-step annotated figures;
- biology structures and process diagrams;
- chemistry particle or reaction sketches;
- physics force, circuit, wave, and energy-transfer diagrams;
- economics curves, flow diagrams, and scenario posters;
- text-heavy infographics in the selected output language, with official
  formulae and syllabus terms preserved when needed.

Use image generation as a user-selected illustration adapter, not as the source
of truth. The generator should first create source-bound knowledge points and
practice examples, then analyze which items need visual explanation. Simple
visuals can use SVG; complex infographics should become source-bound visual
briefs and prompt-queue entries unless the user has supplied a callable image
route.

The base handbook pipeline does not require an image model. Supported visual
routes are:

- external GPT Image 2.0 workflows
- external Qwen Image 2.0 Pro workflows
- external SenseNova U1 Fast workflows
- `custom`
- `deterministic-svg` for SVG-safe visuals only
- `prompt-queue` as the default route with prompts but no final complex
  infographics

Only run real image generation when the user supplies a callable skill, API,
script, generated asset directory, or custom provider configuration. For
`custom`, collect only:

- model name;
- endpoint URL;
- API-key environment variable name.

Never collect the raw key in chat, docs, screenshots, or committed files.

The guide should also support lively explanation styles. A model-generated
visual can be paired with a life-scene story, detective-style reasoning, or an
anime-quest style mission. These modes should use original framing by default
and should not copy protected characters, dialogue, or fictional worlds.

## Scripted Scientific-Vector Fallback

The project can borrow the useful part of
[`nature-figure`](https://github.com/Yuan1z0825/nature-skills/tree/main/skills/nature-figure)
without depending on that repository at runtime. When no callable image model is
available, exact chart-like visuals should be treated as scientific vector
figures: define the learning claim, required labels, source-bound symbols, and
review risk before drawing, then output editable SVG.

Use this for number lines, axes, probability trees, statistics charts,
distance-time graphs, rate curves, pH scales, energy profiles, and simple
labelled geometry. Do not use it for rich educational posters, dense lab
apparatus, complex economics scenarios, or text-heavy infographics; those remain
prompt-queue items until a reviewed asset is supplied.

## Recommended Providers

| Provider | Best use | Notes |
|---|---|---|
| GPT Image 2.0 | High-quality option for OpenAI-compatible workflows, visual explanations, edits, and polished guide illustrations. | Treat it as an external capability unless the user has a callable route. Check cost, moderation, and organization requirements. |
| Qwen-Image-2.0 / Qwen Image 2.0 Pro | Chinese or English text-heavy infographics, poster-like layouts, PPT-style visual explanations, and China-market experiments. | Treat API availability, provider endpoint, license, and deployment constraints as configurable. |
| SenseNova U1 Fast | Fast infographic drafts, local/provider experiments, dense visual communication, and interleaved image-text tests. | Use as an experimental provider until this project has its own visual benchmark set. |

Do not hard-code one provider and do not imply these providers are available to
every user. Use a provider interface so schools, tutors, or agents can choose
based on availability, cost, privacy, and language quality.

## Suggested Architecture

Use this as the integration flow:

```text
official specification
  -> extracted syllabus points
  -> deterministic guide plan
  -> visual-need analysis
  -> SVG if simple, or prompt queue if complex
  -> visual_brief prompt queue
  -> reviewed illustration asset when a callable route or imported asset exists
  -> HTML/PDF guide
```

Recommended interface:

```text
generate_illustration(
  provider_config,
  topic_id,
  topic_title,
  source_snippet_ids,
  visual_type,
  required_labels,
  forbidden_claims,
  language_policy,
  output_size
)
```

Each generated image should store:

- model/provider name;
- prompt;
- source topic and source snippets;
- generation time;
- caption and alt text;
- review status;
- whether it is safe for student-facing use.

## Importing External Assets

The open-source repository does not hard-code private image APIs. If an agent or
teacher generates infographic files with GPT Image, Qwen Image, SenseNova U1
Fast, or a custom provider, name each file with the manifest ID, for example:

```text
visual_001.png
visual_002_market-equilibrium.png
visual_003.webp
```

For local environments that have a compatible `image-gen-flow` GPT Image 2
local Router installed, pending showcase images can be generated directly
after Ethan confirms the route and parameters:

```bash
python scripts/generate_pending_infographics_router.py ./outputs/mathematics-9260-sample ./outputs/economics-9214-sample ./outputs/chemistry-9202-sample --size 1536x1024 --quality high --output-format png
```

This helper reads the API key from `YAIROUTER_API_KEY`, writes prompts and
responses under each guide's `images/` directory, and updates
`visual_manifest.json`. Do not commit the key or paste it into prompts.

Then import them into the guide package:

```bash
python scripts/import_infographic_assets.py ./outputs/chemistry-9202 \
  --asset-dir ./generated-infographics/chemistry-9202 \
  --provider "gpt-image-2"
```

The script copies matching raster images into `images/`, updates
`images/visual_manifest.json`, and marks imported entries as generated. After
import, regenerate/finalize the guide so the HTML/PDF uses the images:

```bash
python scripts/finalize_release_samples.py --outputs-root ./outputs
python scripts/verify_release_samples.py --outputs-root ./outputs
```

## Routing Rules

- Use deterministic SVG for knowledge maps, topic dependency diagrams, and
  source-bound structure.
- Use GPT Image 2.0 when the user wants polished guide illustrations and a
  callable OpenAI-compatible image route is available.
- Use Qwen-Image-2.0 or Qwen Image 2.0 Pro when Chinese typography or
  text-heavy infographic layout is the main evaluation point.
- Use SenseNova U1 Fast for fast infographic drafts, local experiments, or
  low-latency provider tests.
- Do not recreate official exam paper diagrams, mark scheme diagrams, or
  copyrighted textbook illustrations.
- Do not add labels, mechanisms, equations, or facts that are absent from the
  extracted specification unless a subject expert reviews them.

## Prompt Template

```text
Create an educational illustration for an International GCSE or International
AS-A-level revision guide.

Exam board: {exam_board}
Qualification: {qualification_title}
Topic: {topic_title}
Source-bound learning point: {source_point}
Visual type: {visual_type}
Required labels: {required_labels}
Language policy: use the selected output language for labels; preserve official
formulae, symbols, and reviewed syllabus terms when needed.

Make it clear, printable, student-friendly, and suitable for a revision guide.
Do not add new syllabus facts, named examples, equations, or exam claims beyond
the source point.
```

## 中文

复习手册的核心事实不应该依赖生图模型。当前 MVP 使用确定性 SVG 知识地图，是因为
它们更容易追溯到官方大纲点。

但很多知识点确实需要更好的视觉解释，例如：

- Science 实验装置和安全布局；
- Biology 结构图和过程图；
- Chemistry 粒子模型、反应过程示意图；
- Physics 力、电路、波、能量转移图；
- Economics 曲线图、流程图、场景信息图；
- 按用户选择的输出语言生成的文字信息图，必要时保留公式、符号和经复核的官方术语。

生图应该是可选插图层，不是事实来源。生成器应先根据大纲生成基础知识点和
例题，再分析哪些知识点或例题需要图文结合讲解。简单图用 SVG；复杂信息图默认
进入 source-bound visual brief 和 prompt queue。

基础手册生成不要求用户先提供生图服务。不要把下面这些选项做成生成前的
用户菜单；它们只是基础手册完成后、发现复杂信息图需求时可考虑的外部路线：

- GPT Image 2.0 外部工作流
- Qwen Image 2.0 Pro 外部工作流
- SenseNova U1 Fast 外部工作流
- `custom`
- `deterministic-svg`：只用于 SVG 安全图
- `prompt-queue`：默认路线，生成提示词队列，不代表复杂信息图已经完成

只有用户提供可调用的生图 Skill、API、脚本、生成后的图片目录或 custom provider
配置时，才进行真实图片生成或导入。

如果选择 `custom`，只记录模型名、接口 URL、API key 所在的环境变量名。不要让用户
在聊天、文档、截图或仓库里暴露真实 key。

## 推荐模型

| Provider | 适合场景 | 备注 |
|---|---|---|
| GPT Image 2.0 | OpenAI-compatible 工作流里的高质量选项，适合复习手册插图、视觉解释和编辑。 | 只有用户有可调用路线时才使用；注意成本、内容审核和组织要求。 |
| Qwen-Image-2.0 / Qwen Image 2.0 Pro | 中文或英文文字较多的信息图、海报式解释、PPT 风格知识图、国内场景实验。 | API、服务商、许可和部署限制应做成配置，不要写死。 |
| SenseNova U1 Fast | 快速信息图草稿、本地或自定义 provider 实验、密集图文表达测试。 | 在本项目建立自己的视觉基准前，建议作为实验性 provider。 |

不要把项目绑定到单一 provider。更好的做法是设计一个 provider interface，让学校、
老师、家长或 agent 按可用性、成本、隐私和所选语言的排版质量来选择。

## 生成边界

- 知识地图、topic 依赖关系和 source-bound 结构优先用确定性 SVG。
- 需要精美插图且用户有可调用 OpenAI-compatible 图像路线时，可以评估 GPT Image 2.0。
- 需要中文排版或文字密集型信息图时，可以评估 Qwen-Image-2.0 / Qwen Image 2.0 Pro。
- 需要快速信息图草稿、本地实验或低延迟 provider 测试时，可以评估 SenseNova U1 Fast。
- 不要复刻官方真题图、mark scheme 图或教材版权插图。
- 不要让图片添加 specification 中没有的标签、机制、公式或考试结论，除非经过学科老师复核。
