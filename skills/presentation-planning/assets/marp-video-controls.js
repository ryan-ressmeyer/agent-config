// Marp video controls — paused-then-play and autoplay-on-entry.
//
// Implements two attributes on <video> tags inside slides.md:
//
//   data-play-from-start   Autoplay from frame 0 when the slide becomes active.
//                          Pause + rewind when the slide becomes inactive.
//
//   data-play-then-advance Show frame 0 on entry. The next advance keypress on
//                          this slide PLAYS the video (and is consumed — does
//                          not advance to the next slide). The press after that
//                          advances normally. Going back resets the played flag
//                          so the same slide replays on next visit.
//
// Why both: data-play-from-start is for slides where the speaker wants the
// video already running on arrival. data-play-then-advance is for slides where
// the speaker wants to land on a still frame, deliver a setup line, and then
// trigger playback at a deliberate moment — without needing to duplicate the
// slide.
//
// Implementation notes (do not "simplify" without re-reading these):
//
//   * Marp's bespoke presenter renders each slide as an <svg> wrapping a
//     <foreignObject> wrapping a <section>. The bespoke-marp-active /
//     bespoke-marp-slide classes are applied to the <svg>, NOT the <section>.
//     We must therefore match by class only (".bespoke-marp-active"), never by
//     element name ("section.bespoke-marp-active" matches nothing).
//
//   * The keydown listener is registered with capture: true so it runs before
//     bespoke's bubble-phase handler. stopImmediatePropagation() is required
//     to prevent bespoke from advancing on the same keypress.
//
//   * Do NOT call v.load() before play(). load() unloads the current resource,
//     which drops the element's intrinsic aspect ratio for one frame — the
//     video collapses to the HTML5 default 300x150 and surrounding content
//     reflows visibly. currentTime = 0 is sufficient on a video that already
//     has its first frame painted.

(function () {
  const ACTIVE_CLASS = "bespoke-marp-active";
  const SLIDE_CLASS = "bespoke-marp-slide";
  const ADVANCE_KEYS = new Set([
    "ArrowRight", "ArrowDown", "PageDown", "Enter", " ", "Spacebar"
  ]);
  const LOG = (...args) => console.debug("[marp-video]", ...args);

  function activeSlide() {
    return document.querySelector("." + ACTIVE_CLASS);
  }

  function pendingPlayThenAdvance(slide) {
    if (!slide) return null;
    const vids = slide.querySelectorAll("video[data-play-then-advance]");
    for (const v of vids) {
      if (v.dataset.ptaPlayed !== "1") return v;
    }
    return null;
  }

  function startVideo(v, label) {
    LOG(label, "starting", { src: v.currentSrc || v.src, readyState: v.readyState, paused: v.paused, muted: v.muted });
    const onPlay = () => LOG(label, "play event fired");
    const onError = (ev) => LOG(label, "error event:", v.error, ev);
    v.addEventListener("play", onPlay, { once: true });
    v.addEventListener("error", onError, { once: true });
    try { v.currentTime = 0; } catch (e) { LOG(label, "currentTime=0 threw", e); }
    const p = v.play();
    if (p && typeof p.then === "function") {
      p.then(() => LOG(label, "play() resolved"))
       .catch((err) => LOG(label, "play() rejected:", err && (err.name + ": " + err.message)));
    }
  }

  document.addEventListener("keydown", (e) => {
    if (!ADVANCE_KEYS.has(e.key)) return;
    if (e.metaKey || e.ctrlKey || e.altKey) return;
    const slide = activeSlide();
    const v = pendingPlayThenAdvance(slide);
    if (!v) return;
    e.preventDefault();
    e.stopImmediatePropagation();
    v.dataset.ptaPlayed = "1";
    startVideo(v, "play-then-advance");
  }, true);

  function sync() {
    const targets = document.querySelectorAll(
      "video[data-play-from-start], video[data-play-then-advance]"
    );
    targets.forEach((v) => {
      const slide = v.closest("." + SLIDE_CLASS);
      const active = !!(slide && slide.classList.contains(ACTIVE_CLASS));
      const playFromStart = v.hasAttribute("data-play-from-start");
      const playThenAdvance = v.hasAttribute("data-play-then-advance");
      if (active) {
        if (playFromStart) startVideo(v, "play-from-start");
      } else {
        try { v.pause(); v.currentTime = 0; } catch (_) {}
        if (playThenAdvance) delete v.dataset.ptaPlayed;
      }
    });
  }

  const obs = new MutationObserver(sync);
  obs.observe(document.body, { subtree: true, attributes: true, attributeFilter: ["class"] });
  window.addEventListener("load", sync);
  document.addEventListener("DOMContentLoaded", sync);
  sync();
})();
