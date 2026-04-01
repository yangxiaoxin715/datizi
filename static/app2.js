// 搭梯子 2.0 — app2.js

(function () {
  // ── State ──────────────────────────────────────────
  let selectedGrade = "";
  let selectedSource = "";
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
  let estimatedMs = 35000; // 默认值，classify 后会更新

  const PHASES = [
    { label: "正在理解这道题…",   until: 0.20 },
    { label: "分析孩子的卡点…",   until: 0.45 },
    { label: "整理讲题思路…",     until: 0.70 },
    { label: "生成讲题方案中…",   until: 1.00 },
  ];

  function startProgress(estimatedSeconds) {
    estimatedMs = estimatedSeconds * 1000;
    const startTime = Date.now();
    progressFill.style.width = "0%";
    loadingBox.classList.add("visible");
    submitBtn.style.display = "none";

    progressTimer = setInterval(() => {
      const elapsed = Date.now() - startTime;
      const ratio = Math.min(elapsed / estimatedMs, 1);
      // 缓动到最多 88%，留给实际完成时跳 100%
      const pct = Math.min(88, Math.round(Math.sqrt(ratio) * 88));
      progressFill.style.width = pct + "%";

      // 阶段文案（不再出现"快好了"）
      const phase = PHASES.find(p => ratio <= p.until) || PHASES[PHASES.length - 1];
      loadingLabel.textContent = phase.label;

      // 倒计时：有剩余时显示秒数，超出预估则只说"还在生成中…"
      const remaining = Math.round((estimatedMs - elapsed) / 1000);
      if (remaining > 3) {
        loadingSubLabel.textContent = "预计还需 " + remaining + " 秒";
      } else if (remaining > 0) {
        loadingSubLabel.textContent = "马上就好…";
      } else {
        loadingSubLabel.textContent = "还在生成中，再等一下…";
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

  // ── Source selection ───────────────────────────────
  const sourceButtons = document.querySelectorAll(".source-btn");
  sourceButtons.forEach(btn => {
    btn.addEventListener("click", () => {
      sourceButtons.forEach(b => b.classList.remove("selected"));
      btn.classList.add("selected");
      selectedSource = btn.dataset.source;
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

    const payload = {
      grade: selectedGrade,
      question: questionInput.value.trim(),
      student_answer: studentInput.value.trim(),
      parent_note: parentInput.value.trim(),
      source: selectedSource,
    };

    // Step 1: classify (instant, local rules on server)
    let chosenModel = "";
    let estimatedSeconds = 35;
    try {
      const cr = await fetch("/api/v2/classify", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const cj = await cr.json();
      chosenModel = cj.model || "";
      estimatedSeconds = cj.estimated_seconds || 35;
    } catch (_) {
      // classify 失败不影响主流程，用默认值
    }

    startProgress(estimatedSeconds);

    try {
      const resp = await fetch("/api/v2/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ...payload, model: chosenModel }),
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
      // 不把浏览器底层英文报错直接展示给用户
      const isNetworkErr = !err.message || err.message === "Failed to fetch"
        || err.message.toLowerCase().includes("network")
        || err.message.toLowerCase().includes("pattern")
        || err.message.toLowerCase().includes("load");
      errorBanner.textContent = isNetworkErr
        ? "网络连接出了点问题，请重新点一次「生成讲题方案」。"
        : (err.message || "生成失败，请稍后再试。");
      errorBanner.classList.add("visible");
    } finally {
      submitBtn.disabled = false;
    }
  });

  // ── Helpers ────────────────────────────────────────
  function escapeHtml(str) {
    return str.replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;");
  }

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

    // Module 4: key_scripts
    const ks = data.key_scripts || {};
    document.getElementById("m-script-open").textContent   = ks.open        || "";
    document.getElementById("m-script-stuck").textContent  = ks.when_stuck  || "";
    document.getElementById("m-script-verify").textContent = ks.verify       || "";

    // Module 5: wrong_answer_responses
    const warBox = document.getElementById("m-wrong-answers");
    warBox.innerHTML = "";
    const wars = Array.isArray(data.wrong_answer_responses) ? data.wrong_answer_responses : [];
    wars.forEach(item => {
      const div = document.createElement("div");
      div.className = "wrong-answer-item";
      div.innerHTML =
        `<div class="child-says">孩子说：<strong>${escapeHtml(item.child_says || "")}</strong></div>` +
        `<div class="parent-says">${escapeHtml(item.parent_says || "")}</div>`;
      warBox.appendChild(div);
    });

    // Module 6: parent_traps
    const trapList = document.getElementById("m-traps");
    trapList.innerHTML = "";
    const traps = Array.isArray(data.parent_traps) ? data.parent_traps : [];
    traps.forEach(t => {
      const li = document.createElement("li");
      li.textContent = t;
      trapList.appendChild(li);
    });

    // Module 7: three_steps
    const ts = data.three_steps || {};
    document.getElementById("m-say-it").textContent   = ts.say_it   || "";
    document.getElementById("m-write-it").textContent = ts.write_it || "";
    document.getElementById("m-draw-it").textContent  = ts.draw_it  || "";
  }

  // ── Back button ────────────────────────────────────
  btnBack.addEventListener("click", () => {
    gradeButtons.forEach(b => b.classList.remove("selected"));
    sourceButtons.forEach(b => b.classList.remove("selected"));
    selectedGrade = "";
    selectedSource = "";
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
    const ks = d.key_scripts || {};
    const stuckText = Array.isArray(d.stuck_points)
      ? d.stuck_points.map(p => "• " + p).join("\n")
      : "• " + d.stuck_points;
    const warText = Array.isArray(d.wrong_answer_responses)
      ? d.wrong_answer_responses.map(w => "孩子说：" + w.child_says + "\n你说：" + w.parent_says).join("\n\n")
      : "";
    const trapText = Array.isArray(d.parent_traps)
      ? d.parent_traps.map(t => "× " + t).join("\n")
      : "";

    const text = [
      "【这题先讲什么】\n" + d.start_from,
      "【孩子最容易卡在哪】\n" + stuckText,
      "【如果孩子没懂，退回哪一步】\n" + d.fallback_step,
      "【你现在可以直接这样说】\n开口第一句：" + ks.open + "\n孩子卡住时：" + ks.when_stuck + "\n检验听懂了没：" + ks.verify,
      warText ? "【当孩子这样说，你这样接】\n" + warText : "",
      trapText ? "【这样说会让孩子更乱】\n" + trapText : "",
      "【讲明白三步】\n先说出来：" + ts.say_it + "\n再写出来：" + ts.write_it + "\n必要时画出来：" + ts.draw_it,
    ].filter(Boolean).join("\n\n");

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
