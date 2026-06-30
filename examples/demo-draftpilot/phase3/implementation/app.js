const assetBase = "../../phase2/assets/icons";

const mockOnboardingSteps = [
  {
    id: "brand-voice",
    title: "Add brand voice",
    description: "Teach DraftPilot how your company sounds before it writes a line.",
    status: "active",
    icon: "brand-voice.svg"
  },
  {
    id: "connect-website",
    title: "Connect website",
    description: "Pull product proof points, testimonials, and service details into the workspace.",
    status: "upcoming",
    icon: "connect-website.svg"
  },
  {
    id: "create-campaign",
    title: "Create first campaign",
    description: "Turn your setup into a launch announcement with a clear CTA.",
    status: "upcoming",
    icon: "create-campaign.svg"
  }
];

const stepsContainer = document.querySelector("#steps");
const setupCount = document.querySelector("#setupCount");
const primaryAction = document.querySelector("#primaryAction");
const campaignType = document.querySelector("#campaignType");
const campaignTypeButton = document.querySelector("#campaignTypeButton");
const demoModal = document.querySelector("#demoModal");
const openModal = document.querySelector("#openModal");
const closeModal = document.querySelector("#closeModal");

function renderSteps() {
  stepsContainer.innerHTML = "";

  mockOnboardingSteps.forEach((step, index) => {
    const button = document.createElement("button");
    button.className = "setup-step";
    button.type = "button";
    button.dataset.status = step.status;
    button.setAttribute("aria-label", `${step.title}: ${step.description}`);

    button.innerHTML = `
      <span class="step-icon" aria-hidden="true">
        <img src="${assetBase}/${step.icon}" alt="" />
      </span>
      <span class="step-copy">
        <strong>${step.title}</strong>
        <span>${step.description}</span>
      </span>
      <span class="step-status">${step.status === "active" ? "Start" : `Step ${index + 1}`}</span>
    `;

    button.addEventListener("click", () => {
      mockOnboardingSteps.forEach((item) => {
        item.status = item.id === step.id ? "active" : "upcoming";
      });
      setupCount.textContent = `${index + 1} of ${mockOnboardingSteps.length} active`;
      renderSteps();
    });

    stepsContainer.append(button);
  });
}

primaryAction.addEventListener("click", () => {
  primaryAction.textContent = "Campaign draft started";
  window.setTimeout(() => {
    primaryAction.textContent = "Create first campaign";
  }, 1400);
});

campaignTypeButton.addEventListener("click", () => {
  campaignType.classList.toggle("is-open");
});

openModal.addEventListener("click", () => {
  demoModal.classList.remove("is-hidden");
  demoModal.setAttribute("aria-hidden", "false");
  closeModal.focus();
});

closeModal.addEventListener("click", () => {
  demoModal.classList.add("is-hidden");
  demoModal.setAttribute("aria-hidden", "true");
  openModal.focus();
});

demoModal.addEventListener("click", (event) => {
  if (event.target === demoModal) {
    closeModal.click();
  }
});

renderSteps();
