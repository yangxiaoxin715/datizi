// 搭梯子 2.0 — app2.js

(function () {
  // ── State ──────────────────────────────────────────
  let selectedGrade = "";
  let lastResult = null;
  let progressTimer = null;

  // ── DOM refs ───────────────────────────────────────
  const viewInput  = document.getElementById("view-input");
  const viewResult = document.getElementById("view-result");

  const gradeButtons  = document.querySelectorAll(".grade-btn");
  const questionInput = document.getElementById("question");
  const studentInput  = document.getElementById("student-answer");
  const parentInput   = document.getElementById("parent-note");
  const submitBtn     = document.getElementById("submit-btn");
  const gradeError    = document.getElementById("grade-error");
  const questionError = document.getElementById("question-error");
  const errorBanner   = document.getElementById("error-banner");

  const loadingBox     = document.getElementById("loading-box");
  const loadingLabel   = document.getElementById("loading-label");
  const progressFill   = document.getElementById("progress-fill");
  const loadingSubLabel = document.getElementById("loading-sublabel");

  const btnBack = document.getElementById("btn-back");
  const btnCopy = document.getElementById("btn-copy");

  // ── Progress bar helpers ───────────────────────────
  // 预估 R1 需要 ~40 秒；进度条用缓动：前半段快，后半段慢，最多到 90%
  const ESTIMATED_MS = 40000;
  const PHASES = [
    { label: "正在理解这道题…",     until: 0.15 },
    { label: "分析孩子的卡点…",     until: 0.40 },
    { label: "整理讲题思路…",       until: 0.65 },
    { label: "生成讲题方案中…",     until: 0.85 },
    { label: "快好了，稍等一下…",   until: 0.90 },
  ];

  function startProgress() {
    const startTime = Date.now();
    progressFill.style.width = "0%";
    loadingBox.classList.add("visible");
    submitBtn.style.display = "none";

    progressTimer = setInterval(() => {
      const elapsed = Date.now() - startTime;
      // 缓动：ratio 越大增长越慢，上限 90%
      const ratio = Math.min(elapsed / ESTIMATED_MS, 1);
      const pct = Math.min(90, Math.round(Math.sqrt(ratio) * 90));
      progressFill.style.width = pct + "%";

      // 阶段文案
      const phase = PHASES.find(p => ratio <= p.until) || PHASES[PHASES.length - 1];
      loadingLabel.textContent = phase.label;

      // 倒计时
      const remaining = Math.max(0, Math.round((ESTIMATED_MS - elapsed) / 1000));
      if (remaining > 0) {
        loadingSubLabel.textContent = "预计还需 " + remaining + " 秒";
      } else {
        loadingSubLabel.textContent = "快好了，请再等一下…";
      }
    }, 500);
  }

  function finishProgress() {
    clearInterval(progressTimer);
    progressFill.style.width = "100%";
    loadingLabel.textContent = "讲题方案已生成 ✓";
    loadingSubLabel.textContent = "";
    setTimeout(() => {
      loadingBox.classList.remove("visible");
      submitBtn.style.display = "block";
    }, 400);
  }

  function resetProgress() {
    clearInterval(progressTimer);
    loadingBox.classList.remove("visible");
    progressFill.style.width = "0%";
    submitBtn.style.display = "block";
  }

  // ── Grade selection ────────────────────────────────
  gradeButtons.forEach(btn => {
    btn.addEventListener("click", () => {
      gradeButtons.forEach(b => b.classList.remove("selected"));
      btn.classList.add("selected");
      selectedGrade = btn.dataset.grade;
      gradeError.classList.remove("visible");
    });
  });

  // ── Form submit ────────────────────────────────────
  submitBtn.addEventListener("click", async () => {
    // Validate
    let valid = true;
    if (!selectedGrade) {
      gradeError.classList.add("visible");
      valid = false;
    }
    if (!questionInput.value.trim()) {
      questionError.classList.add("visible");
      valid = false;
    } else {
      questionError.classList.remove("visible");
    }
    if (!valid) return;

    // Loading state
    submitBtn.disabled = true;
    errorBanner.classList.remove("visible");
    startProgress();

    try {
      const resp = await fetch("/api/v2/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          grade: selectedGrade,
          question: questionInput.value.trim(),
          student_answer: studentInput.value.trim(),
          parent_note: parentInput.value.trim(),
        }),
      });

      const json = await resp.json();

      if (!json.success) {
        throw new Error(json.error || "生成失败，请稍后再试。");
      }

      lastResult = json.data;
      finishProgress();
      renderResult(json.data);
      setTimeout(() => showView("result"), 450);

    } catch (err) {
      resetProgress();
      errorBanner.textContent = err.message || "生成失败，请稍后再试。";
      errorBanner.classList.add("visible");
    } finally {
      submitBtn.disabled = false;
    }
  });

  // ── Render result ──────────────────────────────────
  function renderResult(data) {
    // Module 1: start_from
    document.getElementById("m-start-from").textContent = data.start_from || "";

    // Module 2: stuck_points
    const stuckList = document.getElementById("m-stuck-list");
    stuckList.innerHTML = "";
    const points = Array.isArray(data.stuck_points) ? data.stuck_points : [data.stuck_points];
    points.forEach(p => {
      const li = document.createElement("li");
      li.textContent = p;
      stuckList.appendChild(li);
    });

    // Module 3: fallback_step
    document.getElementById("m-fallback").textContent = data.fallback_step || "";

    // Module 4: direct_script
    document.getElementById("m-script").textContent = data.direct_script || "";

    // Module 5: three_steps
    const ts = data.three_steps || {};
    document.getElementById("m-say-it").textContent   = ts.say_it   || "";
    document.getElementById("m-write-it").textContent = ts.write_it || "";
    document.getElementById("m-draw-it").textContent  = ts.draw_it  || "";
  }

  // ── Back button ────────────────────────────────────
  btnBack.addEventListener("click", () => {
    gradeButtons.forEach(b => b.classList.remove("selected"));
    selectedGrade = "";
    questionInput.value = "";
    studentInput.value  = "";
    parentInput.value   = "";
    gradeError.classList.remove("visible");
    questionError.classList.remove("visible");
    errorBanner.classList.remove("visible");
    resetProgress();
    showView("input");
  });

  // ── Copy result ────────────────────────────────────
  btnCopy.addEventListener("click", async () => {
    if (!lastResult) return;
    const d  = lastResult;
    const ts = d.three_steps || {};
    const stuckText = Array.isArray(d.stuck_points)
      ? d.stuck_points.map(p => "• " + p).join("\n")
      : "• " + d.stuck_points;

    const text = [
      "【这题先讲什么】\n" + d.start_from,
      "【孩子最容易卡在哪】\n" + stuckText,
      "【如果孩子没懂，退回哪一步】\n" + d.fallback_step,
      "【你现在可以直接这样说】\n" + d.direct_script,
      "【讲明白三步】\n先说出来：" + ts.say_it + "\n再写出来：" + ts.write_it + "\n必要时画出来：" + ts.draw_it,
    ].join("\n\n");

    try {
      await navigator.clipboard.writeText(text);
      const orig = btnCopy.textContent;
      btnCopy.textContent = "已复制 ✓";
      setTimeout(() => { btnCopy.textContent = orig; }, 2000);
    } catch {
      // Fallback for browsers that block clipboard API
      const ta = document.createElement("textarea");
      ta.value = text;
      ta.style.position = "fixed";
      ta.style.opacity  = "0";
      document.body.appendChild(ta);
      ta.select();
      document.execCommand("copy");
      document.body.removeChild(ta);
      btnCopy.textContent = "已复制 ✓";
      setTimeout(() => { btnCopy.textContent = "复制这份讲题方案"; }, 2000);
    }
  });

  // ── View toggle ────────────────────────────────────
  function showView(name) {
    viewInput.classList.toggle("active",  name === "input");
    viewResult.classList.toggle("active", name === "result");
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  // Init: show input view
  showView("input");
})();
