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
    points: ["从官网目录发现课程", "读取公开大纲 PDF", "保留来源链接和文件校验"],
  },
  {
    tag: "02",
    title: "Edexcel",
    accent: "#be4750",
    points: ["先支持用户提供官方链接", "IGCSE 和 IAL 样例已通过", "后续再扩展自动目录发现"],
  },
  {
    tag: "03",
    title: "CAIE",
    accent: "#4fa394",
    points: ["先支持用户提供官方链接", "多年份大纲要先确认考试年份", "年份不清楚就先停下确认"],
  },
];

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
  const drift = interpolate([0, 32], [0, -120], Easing.linear)(time);
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
  const orbit = interpolate([0, 6.2], [0, 38], Easing.easeInOutSine)(time);
  return (
    <SceneFrame start={0} end={6.2}>
      <div className="orbit" style={{ transform: `rotate(${orbit}deg) scale(${1 + Math.sin(time * 0.7) * 0.025})` }}></div>
      <div className="kicker">v0.2.3 · 三大考试局支持</div>
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

function PreflightScene() {
  const time = useTime();
  const sourceT = clamp((time - 6.7) / 3.2, 0, 1);
  const rows = [
    ["考试局", "AQA / Edexcel / CAIE"],
    ["科目", "课程阶段、科目名称、代码，或官方链接"],
    ["考试年份", "Cambridge 多年份页面需要先确认"],
    ["输出语言", "中文或英文，开始写作前锁定"],
    ["讲解风格", "严谨、轻松、生活化、故事、侦探、闯关"],
  ];
  return (
    <SceneFrame start={5.7} end={12.0}>
      <div className="kicker">先确认，再生成</div>
      <h2 className="headline">先确认必要信息，再开始生成。</h2>
      <div className="choice-grid">
        <div className="control-panel">
          {rows.map((row, index) => {
            const p = clamp((time - 6.3 - index * 0.18) / 0.55, 0, 1);
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
    <SceneFrame start={11.2} end={18.3}>
      <div className="kicker">三大考试局怎么支持</div>
      <h2 className="headline">各走官方来源，不混用大纲。</h2>
      <p className="lead">AQA 可从官网目录发现课程；Edexcel 和 CAIE 先支持用户提供官方链接或 PDF，后续再扩展自动发现。</p>
      <div className="provider-system">
        {providerData.map((provider, index) => {
          const p = clamp((time - 12.0 - index * 0.28) / 0.75, 0, 1);
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

function SamplesScene() {
  const time = useTime();
  const wallPan = interpolate([18.0, 24.4], [0, -36], Easing.easeInOutSine)(time);
  const stats = [
    ["7", "本地回归样例通过，质量检查无错误"],
    ["357", "跨三大考试局样例生成的知识点讲解"],
    ["318", "带步骤和检查点的例题卡"],
    ["0", "复杂信息图不再假装已生成"],
  ];
  return (
    <SceneFrame start={17.4} end={24.8}>
      <div className="sample-scene">
        <div className="sample-copy">
          <div className="kicker">真实手册样例</div>
          <h2 className="headline">展示的是能交付的复习手册。</h2>
          <div className="stat-list">
            {stats.map((stat, index) => {
              const p = clamp((time - 18.1 - index * 0.18) / 0.55, 0, 1);
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
    <SceneFrame start={24.0} end={29.4}>
      <div className="kicker">图文路线要诚实</div>
      <h2 className="headline">先生成手册，再处理复杂配图。</h2>
      <div className="visual-routing">
        {cards.map((card, index) => {
          const p = clamp((time - 24.7 - index * 0.18) / 0.7, 0, 1);
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

function ClosingScene() {
  const time = useTime();
  const p = clamp((time - 28.5) / 1.0, 0, 1);
  const boxes = ["知识点讲解", "例题卡片", "配图需求", "考试信息"];
  return (
    <SceneFrame start={28.7} end={32}>
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
  const p = `${Math.min(100, (time / 32) * 100)}%`;
  return (
    <div className="footer-mark">
      <span>IGCSE & A-Level AI 复习手册 Skill · v0.2.3</span>
      <div className="progress-line" style={{ "--p": p }}><span></span></div>
      <span>{Math.floor(time).toString().padStart(2, "0")} / 32s</span>
    </div>
  );
}

function App() {
  return (
    <Stage width={1920} height={1080} duration={32} background="#080b10">
      <VideoLabel />
      <Background />
      <IntroScene />
      <PreflightScene />
      <ProviderScene />
      <SamplesScene />
      <VisualRouteScene />
      <ClosingScene />
      <Footer />
    </Stage>
  );
}

ReactDOM.createRoot(document.getElementById("root")).render(<App />);
