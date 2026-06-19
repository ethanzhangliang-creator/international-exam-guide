const { Stage, Sprite, useTime, Easing, interpolate, clamp } = window;

const boardData = [
  {
    name: "AQA",
    note: "Discovers courses from the official catalogue and reads the specification",
    status: "Supported",
    accent: "#d89b33",
  },
  {
    name: "Edexcel",
    note: "Matches official candidates by subject; URL/PDF can pin the exact specification",
    status: "Candidate discovery",
    accent: "#be4750",
  },
  {
    name: "CAIE",
    note: "Matches candidates from the official subject index and confirms exam year",
    status: "Candidate discovery",
    accent: "#4fa394",
  },
];

const providerData = [
  {
    tag: "01",
    title: "AQA",
    accent: "#d89b33",
    points: ["Discover courses from the official catalogue", "Read public specification PDFs", "Keep source URLs and file checks"],
  },
  {
    tag: "02",
    title: "Edexcel",
    accent: "#be4750",
    points: ["Match official candidates by subject name", "Accept official subject pages or specification PDFs", "Return options when candidates are not unique"],
  },
  {
    tag: "03",
    title: "CAIE",
    accent: "#4fa394",
    points: ["Match candidates from the official subject index", "Confirm exam year on multi-year syllabus pages", "Stop and ask when the year is unclear"],
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
      <div className="kicker">v0.2.11 · Three-Board Support</div>
      <h1 className="headline">Three common international exam boards now run in one workflow.</h1>
      <p className="lead">
        AQA, Edexcel, and CAIE share one handbook framework, while each provider reads the syllabus from its own official source.
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
    ["Exam board", "AQA / Edexcel / CAIE"],
    ["Subject", "Qualification level, subject name, code, or official URL"],
    ["Exam year", "Cambridge multi-year pages need confirmation first"],
    ["Output language", "Chinese or English, locked before writing"],
    ["Explanation style", "Serious, light, life-scene, story, detective, or challenge mode"],
  ];
  return (
    <SceneFrame start={5.7} end={12.0}>
      <div className="kicker">Confirm first, then generate</div>
      <h2 className="headline">Confirm the required choices before generation starts.</h2>
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
            <h3>Official subject page</h3>
            <div className="fake-lines"><i></i><i></i><i></i><i></i></div>
          </div>
          <div className="source-card" style={{ left: 124, top: 44, transform: `rotate(${4 - sourceT * 2}deg) translateY(${(1 - sourceT) * 42}px)` }}>
            <h3>Specification PDF</h3>
            <div className="fake-lines"><i></i><i></i><i></i><i></i></div>
          </div>
          <div className="source-card" style={{ left: 214, top: 146, transform: `rotate(${-1 + sourceT * 1.5}deg) translateY(${(1 - sourceT) * 90}px)` }}>
            <h3>Source checks and exam metadata</h3>
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
    <SceneFrame start={12.1} end={17.1}>
      <div className="kicker">How The Three Boards Are Supported</div>
      <h2 className="headline provider-headline">Each board uses its own official source.</h2>
      <p className="lead provider-lead">AQA can discover courses from the official catalogue; Edexcel matches candidates from official pages; CAIE matches from the official subject index. If there is no unique match, the user chooses.</p>
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
    ["7", "local regression samples pass with clean quality checks"],
    ["357", "knowledge explanations generated across the three boards"],
    ["318", "worked-example cards with steps and checkpoints"],
    ["0", "complex infographics are no longer pretended as generated"],
  ];
  return (
    <SceneFrame start={17.4} end={24.1}>
      <div className="sample-scene">
        <div className="sample-copy">
          <div className="kicker">Real Handbook Samples</div>
          <h2 className="headline sample-headline">The samples are deliverable revision handbooks.</h2>
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
            <img src="../three-board-support-video/sample-math-guide.png" alt="Mathematics handbook screenshot" />
          </figure>
          <figure className="shot" style={{ left: 250, top: 250, transform: "rotate(3deg)" }}>
            <img src="../three-board-support-video/sample-economics-guide.png" alt="Economics handbook screenshot" />
          </figure>
          <figure className="shot" style={{ left: 0, top: 455, transform: "rotate(-1deg)" }}>
            <img src="../three-board-support-video/sample-chemistry-guide.png" alt="Chemistry handbook screenshot" />
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
      title: "Count complex visuals first",
      body: "Generate the base handbook first, then report how many complex infographics are needed instead of asking for a model at the start.",
      visual: <div className="svg-diagram"><span></span><span></span><span></span></div>,
    },
    {
      title: "User provides the image route",
      body: "The user may provide an API, Skill, script, designer workflow, or existing image folder; the tool only verifies whether it is actually callable.",
      visual: <div className="queue-lines"><i></i><i></i><i></i><i></i></div>,
    },
    {
      title: "SVG fallback when no model is available",
      body: "Complex infographics get an SVG fallback and a review note; it can aid understanding, but detail errors may be larger.",
      visual: <div className="model-grid"><span>GPT Image 2.0</span><span>Qwen Image 2.0 Pro</span><span>SenseNova U1 Fast</span></div>,
    },
  ];
  return (
    <SceneFrame start={24.4} end={29.3}>
      <div className="kicker">Visual Routing Must Be Honest</div>
      <h2 className="headline route-headline">Generate the handbook first, then handle complex visuals.</h2>
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
  const p = clamp((time - 29.4) / 1.0, 0, 1);
  const boxes = ["Knowledge explanation", "Worked examples", "Visual needs", "Exam metadata"];
  return (
    <SceneFrame start={29.5} end={32}>
      <div className="final-lockup">
        <div>
          <div className="kicker">Handbook Generation Around Official Syllabuses</div>
          <h2 className="headline">Turn official syllabuses into revision handbooks students can actually read.</h2>
          <p className="lead">Three-board support is now in one framework: preserve sources first, then write explanations, examples, visual routes, and HTML/PDF deliverables.</p>
        </div>
        <div className="deliverable" style={{ opacity: p, transform: `rotate(${-1.5 + (1 - p) * -7}deg) translateY(${(1 - p) * 100}px)` }}>
          <h3>International GCSE / AS-A-level Revision Handbook</h3>
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
      <span>IGCSE & A-Level AI Revision Handbook Skill · v0.2.11</span>
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
