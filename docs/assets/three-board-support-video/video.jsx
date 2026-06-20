const { Stage, Sprite, useTime, Easing, interpolate, clamp } = window;

const boardData = [
  {
    name: "AQA",
    note: "可从官网目录发现课程并读取大纲",
    status: "已支持",
    accent: "#d89b33",
  },
  {
    name: "Edexcel",
    note: "根据科目名匹配官方候选，URL/PDF 可精确指定",
    status: "候选发现",
    accent: "#be4750",
  },
  {
    name: "CAIE",
    note: "从官方科目索引匹配候选，并确认考试年份",
    status: "候选发现",
    accent: "#4fa394",
  },
];

const providerData = [
  {
    tag: "01",
    title: "AQA",
    accent: "#d89b33",
    points: ["从官网目录发现课程", "读取公开大纲 PDF", "把大纲转成手册结构"],
  },
  {
    tag: "02",
    title: "Edexcel",
    accent: "#be4750",
    points: ["按科目名匹配官方候选", "支持官方科目页或大纲 PDF 输入", "候选不唯一就返回列表让用户选择"],
  },
  {
    tag: "03",
    title: "CAIE",
    accent: "#4fa394",
    points: ["从官方科目索引匹配候选", "多年份大纲要先确认考试年份", "年份不清楚就先停下确认"],
  },
];

const TOTAL_DURATION = 48;

function useSceneMotion(start, end, inY = 36) {
  const time = useTime();
  const enter = clamp((time - start) / 0.8, 0, 1);
  const exit = clamp((end - time) / 0.55, 0, 1);
  const opacity = Math.min(Easing.easeOutCubic(enter), Easing.easeOutCubic(exit));
  const y = (1 - Easing.easeOutCubic(enter)) * inY + (1 - Easing.easeOutCubic(exit)) * -18;
  return { opacity, transform: `translateY(${y}px)` };
}

function VideoLabel() {
  const time = useTime();
  React.useEffect(() => {
    const label = `${Math.floor(time).toString().padStart(2, "0")}s`;
    document.documentElement.setAttribute("data-screen-label", label);
  }, [Math.floor(time)]);
  return null;
}

function Background() {
  const time = useTime();
  const drift = interpolate([0, TOTAL_DURATION], [0, -150], Easing.linear)(time);
  return (
    <div className="stage">
      <div className="grid-lines" style={{ transform: `translate3d(${drift}px, ${drift * 0.35}px, 0)` }}></div>
      <div className="noise"></div>
    </div>
  );
}

function SceneFrame({ start, end, children }) {
  const motion = useSceneMotion(start, end);
  return (
    <Sprite start={start} end={end} keepMounted={true}>
      <section className="scene" style={motion}>
        {children}
      </section>
    </Sprite>
  );
}

function IntroScene() {
  const time = useTime();
  const cardLift = (index) => {
    const p = clamp((time - 1.2 - index * 0.22) / 0.75, 0, 1);
    return {
      opacity: Easing.easeOutCubic(p),
      transform: `translateY(${(1 - Easing.easeOutBack(p)) * 72}px)`,
      "--accent": boardData[index].accent,
    };
  };
  const orbit = interpolate([0, 5.0], [0, 38], Easing.easeInOutSine)(time);
  return (
    <SceneFrame start={0} end={5.2}>
      <div className="orbit" style={{ transform: `rotate(${orbit}deg) scale(${1 + Math.sin(time * 0.7) * 0.025})` }}></div>
      <div className="kicker">v0.2.18 · 三大考试局支持</div>
      <h1 className="headline">三大常用国际考试局，现在都能跑。</h1>
      <p className="lead">
        AQA、Edexcel、CAIE：同一套复习手册框架，但每个考试局都按自己的官方来源读取大纲。
      </p>
      <div className="hero-board-row">
        {boardData.map((board, index) => (
          <article className="board-card" key={board.name} style={cardLift(index)}>
            <strong>{board.name}</strong>
            <span>{board.note}</span>
            <div className="status">{board.status}</div>
          </article>
        ))}
      </div>
    </SceneFrame>
  );
}

function OriginScene() {
  const time = useTime();
  const notes = [
    ["真实起点", "孩子从中文课堂切换到全英文课堂，不到一年就面对 International GCSE 大考。"],
    ["AI 的任务", "不是替孩子学习，而是把知识点、例题、图解和检查点整理成能读下去的手册。"],
    ["开源目标", "把这套方法做成 Skill，让其他家庭和 Agent 也能按科目生成复习手册。"],
  ];
  return (
    <SceneFrame start={4.8} end={9.7}>
      <div className="kicker">为什么做这个 Skill</div>
      <h2 className="headline provider-headline">先帮一个真实的孩子，把复习压力拆小。</h2>
      <div className="origin-layout">
        <div className="quote-panel">
          <strong>不是替孩子学习，</strong>
          <span>而是把学习路上的噪音降下来。</span>
        </div>
        <div className="story-points">
          {notes.map((note, index) => {
            const p = clamp((time - 5.4 - index * 0.22) / 0.65, 0, 1);
            return (
              <article key={note[0]} style={{ opacity: p, transform: `translateY(${(1 - p) * 34}px)` }}>
                <b>{note[0]}</b>
                <p>{note[1]}</p>
              </article>
            );
          })}
        </div>
      </div>
    </SceneFrame>
  );
}

function UsageScene() {
  const time = useTime();
  const steps = [
    ["01", "把 Skill 链接交给 Agent", "OpenClaw、Hermes 或其他支持 Skill 的 Agent 都可以。"],
    ["02", "说一句需求", "例如：帮我生成 AQA IGCSE Accounting 中文复习手册。"],
    ["03", "确认四件事", "考试局、科目/年份、输出语言、讲解风格。"],
    ["04", "拿到手册", "输出 HTML、PDF、生成记录、图文清单和质量验证。"],
  ];
  return (
    <SceneFrame start={9.4} end={14.4}>
      <div className="kicker">用户怎么用</div>
      <h2 className="headline route-headline">不是安装复杂软件，而是让 Agent 按流程生成手册。</h2>
      <div className="usage-steps">
        {steps.map((step, index) => {
          const p = clamp((time - 10.0 - index * 0.16) / 0.58, 0, 1);
          return (
            <article key={step[0]} style={{ opacity: p, transform: `translateY(${(1 - Easing.easeOutCubic(p)) * 48}px)` }}>
              <div>{step[0]}</div>
              <h3>{step[1]}</h3>
              <p>{step[2]}</p>
            </article>
          );
        })}
      </div>
    </SceneFrame>
  );
}

function PreflightScene() {
  const time = useTime();
  const sourceT = clamp((time - 14.9) / 3.2, 0, 1);
  const rows = [
    ["考试局", "AQA / Edexcel / CAIE"],
    ["科目", "课程阶段、科目名称、代码，或官方链接"],
    ["考试年份", "Cambridge 多年份页面需要先确认"],
    ["输出语言", "中文或英文，开始写作前锁定"],
    ["讲解风格", "严谨、轻松、生活化、故事、侦探、闯关"],
  ];
  return (
    <SceneFrame start={14.1} end={19.1}>
      <div className="kicker">先确认，再生成</div>
      <h2 className="headline">先确认必要信息，再开始生成。</h2>
      <div className="choice-grid">
        <div className="control-panel">
          {rows.map((row, index) => {
            const p = clamp((time - 14.7 - index * 0.18) / 0.55, 0, 1);
            return (
                <div className="choice-row" key={row[0]} style={{ opacity: p, transform: `translateX(${(1 - p) * -34}px)` }}>
                <b>{row[0]}</b>
                <span>{row[1]}</span>
              </div>
            );
          })}
        </div>
        <div className="source-stack">
          <div className="source-card" style={{ left: 34, top: 90, transform: `rotate(${-6 + sourceT * 3}deg) translateY(${(1 - sourceT) * 70}px)` }}>
            <h3>官方科目页</h3>
            <div className="fake-lines"><i></i><i></i><i></i><i></i></div>
          </div>
          <div className="source-card" style={{ left: 124, top: 44, transform: `rotate(${4 - sourceT * 2}deg) translateY(${(1 - sourceT) * 42}px)` }}>
            <h3>考试大纲 PDF</h3>
            <div className="fake-lines"><i></i><i></i><i></i><i></i></div>
          </div>
          <div className="source-card" style={{ left: 214, top: 146, transform: `rotate(${-1 + sourceT * 1.5}deg) translateY(${(1 - sourceT) * 90}px)` }}>
            <h3>来源校验和考试信息</h3>
            <div className="fake-lines"><i></i><i></i><i></i><i></i></div>
          </div>
        </div>
      </div>
    </SceneFrame>
  );
}

function ProviderScene() {
  const time = useTime();
  return (
    <SceneFrame start={18.8} end={23.8}>
      <div className="kicker">三大考试局怎么支持</div>
      <h2 className="headline provider-headline">各走官方来源，不混用大纲。</h2>
      <p className="lead provider-lead">AQA 可从官网目录发现课程；Edexcel 会按官方页面规则匹配候选；CAIE 会从官方科目索引匹配候选。无法唯一确认时，先让用户选。</p>
      <div className="provider-system">
        {providerData.map((provider, index) => {
          const p = clamp((time - 19.2 - index * 0.28) / 0.75, 0, 1);
          return (
            <article className="provider-column" key={provider.title} style={{ "--accent": provider.accent, opacity: p, transform: `translateY(${(1 - Easing.easeOutBack(p)) * 86}px)` }}>
              <div className="tag">{provider.tag}</div>
              <h3>{provider.title}</h3>
              <ul>
                {provider.points.map((point) => <li key={point}>{point}</li>)}
              </ul>
            </article>
          );
        })}
      </div>
    </SceneFrame>
  );
}

function SyllabusScene() {
  const time = useTime();
  const steps = [
    ["官方页面", "找到考试局科目页或用户指定 URL"],
    ["大纲 PDF", "下载公开 specification / syllabus"],
    ["主题拆解", "抽取 topic、assessment、页码和来源片段"],
    ["手册骨架", "生成知识点、例题、复习检查点"],
    ["质量验证", "topic、例题、来源、图文块缺失都会暴露"],
  ];
  return (
    <SceneFrame start={23.5} end={28.3}>
      <div className="kicker">从大纲到手册</div>
      <h2 className="headline route-headline">先守住官方来源，再写成学生能读的内容。</h2>
      <div className="pipeline-board">
        {steps.map((step, index) => {
          const p = clamp((time - 24.0 - index * 0.14) / 0.6, 0, 1);
          return (
            <article className="pipeline-step" key={step[0]} style={{ opacity: p, transform: `translateY(${(1 - p) * 42}px)` }}>
              <b>{String(index + 1).padStart(2, "0")}</b>
              <h3>{step[0]}</h3>
              <p>{step[1]}</p>
            </article>
          );
        })}
      </div>
    </SceneFrame>
  );
}

function LanguageStyleScene() {
  const time = useTime();
  const cards = [
    ["语言锁", "中文或英文先锁定，正文、标签、例题和配图提示不再中英混排。"],
    ["讲解风格", "严谨备考、轻松愉快、生活场景、故事、侦探推理、闯关式。"],
    ["例题生成", "每个 topic 至少有练习卡，带步骤、答案框架、常见失分点。"],
    ["图文判断", "AI 二次分析哪些知识点需要图文结合，而不是全篇堆文字。"],
  ];
  return (
    <SceneFrame start={28.0} end={32.8}>
      <div className="kicker">手册要适合孩子读</div>
      <h2 className="headline provider-headline">语言、语气、例题和图文都要先定规则。</h2>
      <div className="style-grid">
        {cards.map((card, index) => {
          const p = clamp((time - 28.6 - index * 0.16) / 0.58, 0, 1);
          return (
            <article className="style-card" key={card[0]} style={{ opacity: p, transform: `translateX(${(1 - p) * 42}px)` }}>
              <h3>{card[0]}</h3>
              <p>{card[1]}</p>
            </article>
          );
        })}
      </div>
    </SceneFrame>
  );
}

function SamplesScene() {
  const time = useTime();
  const wallPan = interpolate([38.5, 43.0], [0, -36], Easing.easeInOutSine)(time);
  const stats = [
    ["7", "本地回归样例通过，质量检查无错误"],
    ["357", "跨三大考试局样例生成的知识点讲解"],
    ["318", "带步骤和检查点的例题卡"],
    ["0", "复杂信息图不再假装已生成"],
  ];
  return (
    <SceneFrame start={38.0} end={43.1}>
      <div className="sample-scene">
        <div className="sample-copy">
          <div className="kicker">真实手册样例</div>
          <h2 className="headline sample-headline">展示的是能交付的复习手册。</h2>
          <div className="stat-list">
            {stats.map((stat, index) => {
              const p = clamp((time - 38.7 - index * 0.18) / 0.55, 0, 1);
              return (
                <div className="stat" key={stat[1]} style={{ opacity: p, transform: `translateX(${(1 - p) * -32}px)` }}>
                  <b>{stat[0]}</b>
                  <span>{stat[1]}</span>
                </div>
              );
            })}
          </div>
        </div>
        <div className="screenshot-wall" style={{ transform: `translateX(${wallPan}px)` }}>
          <figure className="shot" style={{ left: 80, top: 20, transform: "rotate(-5deg)" }}>
            <img src="sample-math-guide.png" alt="数学手册截图" />
          </figure>
          <figure className="shot" style={{ left: 250, top: 250, transform: "rotate(3deg)" }}>
            <img src="sample-economics-guide.png" alt="经济学手册截图" />
          </figure>
          <figure className="shot" style={{ left: 0, top: 455, transform: "rotate(-1deg)" }}>
            <img src="sample-chemistry-guide.png" alt="化学手册截图" />
          </figure>
        </div>
      </div>
    </SceneFrame>
  );
}

function VisualRouteScene() {
  const time = useTime();
  const cards = [
    {
      title: "先统计复杂图数量",
      body: "基础手册先跑完，再告诉用户需要多少张复杂信息图，不在开始阶段要求用户选择模型。",
      visual: <div className="svg-diagram"><span></span><span></span><span></span></div>,
    },
    {
      title: "用户自行提供方式",
      body: "用户可以给 API、Skill、脚本、设计师流程或已生成图片目录；工具只负责验证是否真的可调用。",
      visual: <div className="queue-lines"><i></i><i></i><i></i><i></i></div>,
    },
    {
      title: "没有模型就 SVG 兜底",
      body: "复杂信息图会生成 SVG 兜底图并标注需要复核；它能帮助理解，但细节误差可能更大。",
      visual: <div className="model-grid"><span>GPT Image 2.0</span><span>Qwen Image 2.0 Pro</span><span>SenseNova U1 Fast</span></div>,
    },
  ];
  return (
    <SceneFrame start={32.5} end={38.2}>
      <div className="kicker">图文路线要诚实</div>
      <h2 className="headline route-headline">先生成手册，再处理复杂配图。</h2>
      <div className="visual-routing">
        {cards.map((card, index) => {
          const p = clamp((time - 33.0 - index * 0.18) / 0.7, 0, 1);
          return (
            <article className="route-card" key={card.title} style={{ opacity: p, transform: `translateY(${(1 - Easing.easeOutCubic(p)) * 58}px)` }}>
              <h3>{card.title}</h3>
              <div className="route-visual">{card.visual}</div>
              <p>{card.body}</p>
            </article>
          );
        })}
      </div>
    </SceneFrame>
  );
}

function QualityScene() {
  const time = useTime();
  const metrics = [
    ["topics", "知识点覆盖"],
    ["practice", "例题覆盖"],
    ["svg_fallback", "SVG 兜底图"],
    ["pending_images", "待外部信息图"],
  ];
  return (
    <SceneFrame start={42.8} end={46.2}>
      <div className="kicker">交付前做验证</div>
      <h2 className="headline provider-headline">不是生成完就算，质量摘要会把问题暴露出来。</h2>
      <div className="quality-grid">
        {metrics.map((metric, index) => {
          const p = clamp((time - 43.3 - index * 0.12) / 0.5, 0, 1);
          return (
            <article className="quality-card" key={metric[0]} style={{ opacity: p, transform: `scale(${0.92 + p * 0.08})` }}>
              <b>{metric[0]}</b>
              <span>{metric[1]}</span>
              <i></i>
            </article>
          );
        })}
      </div>
    </SceneFrame>
  );
}

function ClosingScene() {
  const time = useTime();
  const p = clamp((time - 46.0) / 1.0, 0, 1);
  const boxes = ["知识点讲解", "例题卡片", "配图需求", "考试信息"];
  return (
    <SceneFrame start={45.8} end={TOTAL_DURATION}>
      <div className="final-lockup">
        <div>
          <div className="kicker">围绕官方大纲生成手册</div>
          <h2 className="headline">把官方大纲，变成孩子看得下去的复习手册。</h2>
          <p className="lead">三大考试局支持已进入同一框架：先守住来源，再写出知识点、例题、图文路线和 HTML/PDF 交付。</p>
        </div>
        <div className="deliverable" style={{ opacity: p, transform: `rotate(${-1.5 + (1 - p) * -7}deg) translateY(${(1 - p) * 100}px)` }}>
          <h3>International GCSE / AS-A-level 复习手册</h3>
          <div className="bar"></div>
          <div className="paper-grid">
            {boxes.map((box) => (
              <div className="paper-box" key={box}>
                <b>{box}</b>
                <i></i><i></i><i></i>
              </div>
            ))}
          </div>
        </div>
      </div>
    </SceneFrame>
  );
}

function Footer() {
  const time = useTime();
  const p = `${Math.min(100, (time / TOTAL_DURATION) * 100)}%`;
  return (
    <div className="footer-mark">
      <span>IGCSE & A-Level AI 复习手册 Skill · v0.2.18</span>
      <div className="progress-line" style={{ "--p": p }}><span></span></div>
      <span>{Math.floor(time).toString().padStart(2, "0")} / {TOTAL_DURATION}s</span>
    </div>
  );
}

function App() {
  return (
    <Stage width={1920} height={1080} duration={TOTAL_DURATION} background="#080b10">
      <VideoLabel />
      <Background />
      <IntroScene />
      <OriginScene />
      <UsageScene />
      <PreflightScene />
      <ProviderScene />
      <SyllabusScene />
      <LanguageStyleScene />
      <VisualRouteScene />
      <SamplesScene />
      <QualityScene />
      <ClosingScene />
      <Footer />
    </Stage>
  );
}

ReactDOM.createRoot(document.getElementById("root")).render(<App />);
