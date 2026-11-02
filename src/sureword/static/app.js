/**
 * Sureword Client Application Logic
 */

let currentDraftId = null;
let currentVersion = 1;
let mediaRecorder = null;
let audioChunks = [];
let recordTimerInterval = null;
let recordStartTime = 0;
let isClarifyingField = null;

// DOM Elements
const providerBadge = document.getElementById("provider-badge");
const stateBadge = document.getElementById("state-badge");
const versionBadge = document.getElementById("version-badge");
const recordBtn = document.getElementById("record-btn");
const recordText = document.getElementById("record-text");
const recordingTimer = document.getElementById("recording-timer");
const audioFileInput = document.getElementById("audio-file-input");
const uploadBtn = document.getElementById("upload-btn");
const statusMessage = document.getElementById("status-message");
const transcriptContent = document.getElementById("transcript-content");
const transcriptMeta = document.getElementById("transcript-meta");
const newDraftBtn = document.getElementById("new-draft-btn");
const clarificationBanner = document.getElementById("clarification-banner");
const clarifyFieldTitle = document.getElementById("clarify-field-title");
const clarifyPromptText = document.getElementById("clarify-prompt-text");
const playTtsBtn = document.getElementById("play-tts-btn");
const clarifyMicBtn = document.getElementById("clarify-mic-btn");
const clarifyManualInput = document.getElementById("clarify-manual-input");
const clarifySaveBtn = document.getElementById("clarify-save-btn");
const commitBtn = document.getElementById("commit-btn");
const commitValidationInfo = document.getElementById("commit-validation-info");
const committedResult = document.getElementById("committed-result");
const savedRecordId = document.getElementById("saved-record-id");
const savedJson = document.getElementById("saved-json");
const ttsAudioPlayer = document.getElementById("tts-audio-player");

const FIELD_KEYS = ["person_name", "age", "village", "visit_date"];

// Initialize
window.addEventListener("DOMContentLoaded", async () => {
  await checkHealth();
  const urlParams = new URLSearchParams(window.location.search);
  const existingDraftId = urlParams.get("draft_id");
  if (existingDraftId) {
    await loadExistingDraft(existingDraftId);
  } else {
    await initNewDraft();
  }
  setupEventListeners();
});

async function loadExistingDraft(draftId) {
  showStatus(`Loading visit draft ${draftId}...`, "info");
  try {
    const res = await fetch(`/api/drafts/${draftId}`);
    if (res.ok) {
      const data = await res.json();
      currentDraftId = data.draft_id;
      currentVersion = data.version;
      renderDraft(data);
      hideStatus();
    } else {
      await initNewDraft();
    }
  } catch (err) {
    await initNewDraft();
  }
}

async function checkHealth() {
  try {
    const res = await fetch("/healthz");
    const data = await res.json();
    if (data.gnani_configured) {
      providerBadge.textContent = "Gnani Live (Prisma+Timbre)";
      providerBadge.className = "badge badge-live";
    } else {
      providerBadge.textContent = "Deterministic Fixture Mode";
      providerBadge.className = "badge badge-fixture";
    }
  } catch (err) {
    providerBadge.textContent = "Offline";
    providerBadge.className = "badge badge-warning";
  }
}

async function initNewDraft() {
  showStatus("Initializing visit draft...", "info");
  try {
    const res = await fetch("/api/drafts", { method: "POST" });
    const data = await res.json();
    currentDraftId = data.draft_id;
    currentVersion = data.version;
    updateStateUI(data.state, currentVersion);
    resetFormUI();
    hideStatus();
  } catch (err) {
    showStatus("Failed to initialize draft: " + err.message, "error");
  }
}

function resetFormUI() {
  committedResult.classList.add("hidden");
  clarificationBanner.classList.add("hidden");
  transcriptContent.textContent = "No audio transcribed yet.";
  transcriptMeta.textContent = "";

  FIELD_KEYS.forEach(key => {
    const input = document.getElementById(`field-${key}`);
    const tag = document.getElementById(`tag-${key}`);
    const reasons = document.getElementById(`reasons-${key}`);
    if (input) input.value = "";
    if (tag) {
      tag.textContent = "Missing";
      tag.className = "status-tag tag-missing";
    }
    if (reasons) reasons.innerHTML = "";
  });

  commitBtn.disabled = true;
  commitValidationInfo.textContent = "Form incomplete. Fill or dictate all 4 fields to save.";
}

function updateStateUI(state, version) {
  stateBadge.textContent = state;
  versionBadge.textContent = `v${version}`;

  stateBadge.className = "badge " + (
    state === "READY_FOR_REVIEW" ? "badge-live" :
    state === "NEEDS_CLARIFICATION" ? "badge-fixture" :
    state === "COMMITTED" ? "badge-live" : "badge-neutral"
  );
}

function renderDraft(draft) {
  currentDraftId = draft.draft_id;
  currentVersion = draft.version;
  updateStateUI(draft.state, currentVersion);

  let allValid = true;

  FIELD_KEYS.forEach(key => {
    const f = draft.fields[key];
    const input = document.getElementById(`field-${key}`);
    const tag = document.getElementById(`tag-${key}`);
    const reasonsDiv = document.getElementById(`reasons-${key}`);

    if (f) {
      if (input && f.canonical_value) {
        input.value = f.canonical_value;
      }
      if (tag) {
        tag.textContent = formatStatus(f.status);
        tag.className = `status-tag tag-${f.status}`;
      }
      if (reasonsDiv) {
        reasonsDiv.innerHTML = f.reasons.length ? f.reasons.join("<br>") : "";
      }

      if (f.status === "missing" || f.status === "needs_repeat" || !f.canonical_value) {
        allValid = false;
      }
    } else {
      allValid = false;
    }
  });

  // Handle Clarification Banner
  if (draft.state === "NEEDS_CLARIFICATION" && draft.active_prompt) {
    clarificationBanner.classList.remove("hidden");
    isClarifyingField = draft.active_prompt.target_field;
    clarifyFieldTitle.textContent = `Clarification Needed: ${formatFieldName(isClarifyingField)}`;
    clarifyPromptText.textContent = draft.active_prompt.prompt_text;
    clarifyManualInput.value = "";
    clarifyManualInput.focus();
  } else {
    clarificationBanner.classList.add("hidden");
    isClarifyingField = null;
  }

  // Handle Commit button
  if (draft.state === "READY_FOR_REVIEW" && allValid) {
    commitBtn.disabled = false;
    commitValidationInfo.textContent = "All 4 fields verified. Review carefully and commit.";
  } else if (draft.state === "COMMITTED") {
    commitBtn.disabled = true;
    commitValidationInfo.textContent = "Record already saved locally.";
  } else {
    commitBtn.disabled = true;
    commitValidationInfo.textContent = "Resolve all fields and clarification before saving.";
  }
}

function formatStatus(status) {
  switch (status) {
    case "missing": return "Missing";
    case "proposed": return "Proposed";
    case "needs_repeat": return "Needs Repeat";
    case "user_confirmed": return "Confirmed ✓";
    case "manually_edited": return "Edited ✎";
    default: return status;
  }
}

function formatFieldName(key) {
  switch (key) {
    case "person_name": return "Person Name";
    case "age": return "Age";
    case "village": return "Village";
    case "visit_date": return "Visit Date";
    default: return key;
  }
}

function showStatus(msg, type = "info") {
  statusMessage.textContent = msg;
  statusMessage.className = `status-box status-${type}`;
  statusMessage.classList.remove("hidden");
}

function hideStatus() {
  statusMessage.classList.add("hidden");
}

function setupEventListeners() {
  newDraftBtn.addEventListener("click", initNewDraft);
  recordBtn.addEventListener("click", toggleRecording);
  uploadBtn.addEventListener("click", handleAudioUpload);

  playTtsBtn.addEventListener("click", playSpokenClarification);
  clarifyMicBtn.addEventListener("click", () => startClarificationRecording(isClarifyingField));
  clarifySaveBtn.addEventListener("click", saveManualClarification);

  commitBtn.addEventListener("click", commitCurrentDraft);

  // Inline input manual edits
  FIELD_KEYS.forEach(key => {
    const input = document.getElementById(`field-${key}`);
    if (input) {
      input.addEventListener("change", (e) => {
        saveFieldManualEdit(key, e.target.value);
      });
    }
  });
}

async function toggleRecording() {
  if (mediaRecorder && mediaRecorder.state === "recording") {
    stopRecording();
  } else {
    startRecording();
  }
}

async function startRecording() {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    audioChunks = [];
    mediaRecorder = new MediaRecorder(stream);

    mediaRecorder.ondataavailable = (e) => {
      if (e.data.size > 0) audioChunks.push(e.data);
    };

    mediaRecorder.onstop = async () => {
      const audioBlob = new Blob(audioChunks, { type: "audio/webm" });
      clearInterval(recordTimerInterval);
      recordingTimer.classList.add("hidden");
      recordBtn.classList.remove("btn-recording");
      recordText.textContent = "Start Recording";

      stream.getTracks().forEach(track => track.stop());

      if (isClarifyingField) {
        await submitClarificationAudio(isClarifyingField, audioBlob);
      } else {
        await submitFullAudio(audioBlob);
      }
    };

    mediaRecorder.start();
    recordStartTime = Date.now();
    recordBtn.classList.add("btn-recording");
    recordText.textContent = "Stop Recording";
    recordingTimer.classList.remove("hidden");

    recordTimerInterval = setInterval(() => {
      const elapsed = Math.floor((Date.now() - recordStartTime) / 1000);
      const mm = String(Math.floor(elapsed / 60)).padStart(2, "0");
      const ss = String(elapsed % 60).padStart(2, "0");
      recordingTimer.textContent = `${mm}:${ss} / 00:20`;

      if (elapsed >= 20) {
        stopRecording();
      }
    }, 500);

  } catch (err) {
    showStatus("Microphone access denied or unsupported: " + err.message, "error");
  }
}

function stopRecording() {
  if (mediaRecorder && mediaRecorder.state === "recording") {
    mediaRecorder.stop();
  }
}

async function startClarificationRecording(fieldKey) {
  if (!fieldKey) return;
  showStatus(`Recording clarification for ${formatFieldName(fieldKey)}...`, "info");
  await startRecording();
}

async function handleAudioUpload() {
  const file = audioFileInput.files[0];
  if (!file) {
    showStatus("Please select an audio file to upload", "error");
    return;
  }
  await submitFullAudio(file);
}

async function submitFullAudio(blobOrFile) {
  showStatus("Normalizing audio and running Gnani Prisma STT...", "info");
  const formData = new FormData();
  formData.append("expected_version", currentVersion);
  formData.append("audio_file", blobOrFile, "recording.webm");

  try {
    const res = await fetch(`/api/drafts/${currentDraftId}/audio`, {
      method: "POST",
      body: formData,
    });

    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || "Server error");
    }

    const data = await res.json();
    transcriptContent.textContent = data.transcript.text;
    transcriptMeta.textContent = `Model: ${data.transcript.effective_model || data.transcript.requested_model} | Latency: ${data.transcript.duration_ms}ms | Source: ${data.transcript.source.toUpperCase()}`;

    renderDraft(data.draft);
    hideStatus();

    if (data.draft.state === "NEEDS_CLARIFICATION") {
      playSpokenClarification();
    }
  } catch (err) {
    showStatus("Audio processing failed: " + err.message, "error");
  }
}

async function submitClarificationAudio(fieldKey, audioBlob) {
  showStatus(`Processing spoken clarification for ${formatFieldName(fieldKey)}...`, "info");
  const formData = new FormData();
  formData.append("target_field", fieldKey);
  formData.append("expected_version", currentVersion);
  formData.append("audio_file", audioBlob, "clarify.webm");

  try {
    const res = await fetch(`/api/drafts/${currentDraftId}/clarify`, {
      method: "POST",
      body: formData,
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || "Clarification failed");
    }
    const updatedDraft = await res.json();
    renderDraft(updatedDraft);
    hideStatus();
  } catch (err) {
    showStatus("Clarification failed: " + err.message, "error");
  }
}

async function saveManualClarification() {
  const val = clarifyManualInput.value.trim();
  if (!val || !isClarifyingField) return;
  await saveFieldManualEdit(isClarifyingField, val);
}

async function saveFieldManualEdit(fieldKey, val) {
  if (!val || !val.trim()) return;

  const formData = new FormData();
  formData.append("target_field", fieldKey);
  formData.append("expected_version", currentVersion);
  formData.append("manual_value", val.trim());

  try {
    const res = await fetch(`/api/drafts/${currentDraftId}/clarify`, {
      method: "POST",
      body: formData,
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || "Edit failed");
    }
    const updatedDraft = await res.json();
    renderDraft(updatedDraft);
  } catch (err) {
    showStatus("Failed to update field: " + err.message, "error");
  }
}

async function playSpokenClarification() {
  try {
    playTtsBtn.disabled = true;
    playTtsBtn.textContent = "🔊 Loading...";

    const res = await fetch(`/api/drafts/${currentDraftId}/speech`, { method: "POST" });
    if (!res.ok) throw new Error("TTS generation failed");

    const audioBlob = await res.blob();
    const audioUrl = URL.createObjectURL(audioBlob);
    ttsAudioPlayer.src = audioUrl;
    ttsAudioPlayer.play();

    playTtsBtn.textContent = "🔊 Playing...";
    ttsAudioPlayer.onended = () => {
      playTtsBtn.disabled = false;
      playTtsBtn.textContent = "🔊 Speak";
    };
  } catch (err) {
    playTtsBtn.disabled = false;
    playTtsBtn.textContent = "🔊 Speak";
    showStatus("Could not play spoken prompt: " + err.message, "error");
  }
}

async function commitCurrentDraft() {
  showStatus("Verifying and committing visit record...", "info");
  const idempotencyKey = `idemp_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`;

  try {
    const res = await fetch(`/api/drafts/${currentDraftId}/commit`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        expected_version: currentVersion,
        idempotency_key: idempotencyKey,
      }),
    });

    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || "Commit failed");
    }

    const data = await res.json();
    renderDraft(data.draft);
    savedRecordId.textContent = data.record_id;
    savedJson.textContent = JSON.stringify(data.draft, null, 2);
    committedResult.classList.remove("hidden");
    hideStatus();
  } catch (err) {
    showStatus("Commit failed: " + err.message, "error");
  }
}
