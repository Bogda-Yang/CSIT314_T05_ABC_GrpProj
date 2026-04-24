const userMenu = document.querySelector(".user-menu");
const profileForm = document.querySelector("#profile-form");
const changePasswordForm = document.querySelector("#change-password-form");
const deleteAccountForm = document.querySelector("#delete-account-form");
const avatarInput = document.querySelector("#avatar-input");
const profileAvatarFrame = document.querySelector("#profile-avatar-frame");
const profileAvatarImage = document.querySelector("#profile-avatar-image");
const homeUserAvatar = document.querySelector("#home-user-avatar");
const campaignImagesInput = document.querySelector("#campaign-images-input");
const campaignImagesFileLabel = document.querySelector("#campaign-images-file-label");
const campaignImagesSelectionStatus = document.querySelector("#campaign-images-selection-status");
const campaignCreateDraftForm = document.querySelector("#campaign-create-draft-form");
const campaignBasicForm = document.querySelector("#campaign-basic form");
const campaignGoalForm = document.querySelector("#campaign-goal form");
const campaignDescriptionForm = document.querySelector("#campaign-description form");
const campaignDeadlineForm = document.querySelector("#campaign-deadline form");
const impactRechargeModal = document.querySelector("#impact-recharge-modal");

// 校验密码规则：至少 6 位，且同时包含字母和数字
function validatePasswordPolicy(password) {
  if (password.length < 6) {
    return "Password must be at least 6 characters.";
  }

  const hasLetter = /[A-Za-z]/.test(password);
  const hasDigit = /\d/.test(password);
  if (!hasLetter || !hasDigit) {
    return "Password must contain both letters and numbers.";
  }

  return "";
}

// 打开和关闭右上角用户菜单
if (userMenu) {
  const toggle = userMenu.querySelector(".user-avatar-button");
  const dropdown = userMenu.querySelector(".user-dropdown");

  toggle?.addEventListener("click", () => {
    const willOpen = dropdown.hasAttribute("hidden");
    if (willOpen) {
      dropdown.removeAttribute("hidden");
    } else {
      dropdown.setAttribute("hidden", "");
    }
    toggle.setAttribute("aria-expanded", String(willOpen));
  });

  document.addEventListener("click", (event) => {
    if (!userMenu.contains(event.target)) {
      dropdown?.setAttribute("hidden", "");
      toggle?.setAttribute("aria-expanded", "false");
    }
  });
}

// 统一发送站内账号相关请求
async function postJson(url, payload) {
  const response = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  const data = await response.json();
  if (!response.ok) {
    let message = "Request failed.";

    if (typeof data.detail === "string") {
      message = data.detail;
    } else if (Array.isArray(data.detail) && data.detail.length > 0) {
      message = data.detail
        .map((item) => item.msg || item.message)
        .filter(Boolean)
        .join("; ");
    } else if (typeof data.message === "string") {
      message = data.message;
    }

    throw new Error(message);
  }

  return data;
}

// 设置页面消息提示
function setAccountMessage(node, text, type = "") {
  if (!node) {
    return;
  }
  node.textContent = text;
  node.className = `account-message ${type}`.trim();
}

function formatUsdAmount(value) {
  const numericValue = Number(value) || 0;
  return `$${numericValue.toLocaleString("en-US")}`;
}

// 统一发送文件上传请求
async function postFormData(url, formData) {
  const response = await fetch(url, {
    method: "POST",
    body: formData,
  });

  const data = await response.json();
  if (!response.ok) {
    throw new Error(typeof data.detail === "string" ? data.detail : "Request failed.");
  }

  return data;
}

// 更新页面中的用户头像显示
function updateAvatarUi(avatarUrl) {
  const cacheSafeUrl = avatarUrl ? `${avatarUrl}${avatarUrl.includes("?") ? "&" : "?"}t=${Date.now()}` : "";

  if (profileAvatarFrame) {
    profileAvatarFrame.classList.toggle("has-image", Boolean(avatarUrl));
  }

  if (profileAvatarImage) {
    if (avatarUrl) {
      profileAvatarImage.src = cacheSafeUrl;
      profileAvatarImage.hidden = false;
      profileAvatarImage.removeAttribute("hidden");
    } else {
      profileAvatarImage.src = "";
      profileAvatarImage.hidden = true;
      profileAvatarImage.setAttribute("hidden", "");
    }
  }

  if (homeUserAvatar) {
    if (avatarUrl) {
      homeUserAvatar.classList.add("has-image");
      const existingImage = homeUserAvatar.querySelector("img");
      const existingSvg = homeUserAvatar.querySelector("svg");
      if (existingImage) {
        existingImage.src = cacheSafeUrl;
      } else {
        const image = document.createElement("img");
        image.src = cacheSafeUrl;
        image.alt = "User avatar";
        homeUserAvatar.appendChild(image);
      }
      if (existingSvg) {
        existingSvg.style.display = "none";
      }
    }
  }
}

// 更新个人信息
if (profileForm) {
  const profileMessage = document.querySelector("#profile-message");
  const usernameInput = profileForm.elements.username;
  const ageInput = profileForm.elements.age;

  if (usernameInput) {
    usernameInput.addEventListener("invalid", () => {
      if (usernameInput.validity.valueMissing) {
        usernameInput.setCustomValidity("Please fill out this field.");
      } else {
        usernameInput.setCustomValidity("");
      }
    });

    usernameInput.addEventListener("input", () => {
      usernameInput.setCustomValidity("");
    });
  }

  if (ageInput) {
    ageInput.addEventListener("invalid", () => {
      if (ageInput.validity.rangeOverflow) {
        ageInput.setCustomValidity("Value must be less than or equal to 130.");
      } else {
        ageInput.setCustomValidity("");
      }
    });

    ageInput.addEventListener("input", () => {
      ageInput.setCustomValidity("");
    });
  }

  profileForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const payload = {
      username: profileForm.elements.username.value.trim(),
      gender: profileForm.elements.gender.value.trim(),
      age: profileForm.elements.age.value ? Number(profileForm.elements.age.value) : null,
      occupation: profileForm.elements.occupation.value.trim(),
      contact_details: profileForm.elements.contact_details.value.trim(),
    };

    try {
      setAccountMessage(profileMessage, "Saving profile...");
      const result = await postJson("/api/profile/update", payload);
      profileForm.elements.username.value = result.profile.username;
      profileForm.elements.gender.value = result.profile.gender || "";
      profileForm.elements.age.value = result.profile.age ?? "";
      profileForm.elements.occupation.value = result.profile.occupation || "";
      profileForm.elements.contact_details.value = result.profile.contact_details;
      const profileHeroName = document.querySelector(".profile-hero-name");
      const userDropdownName = document.querySelector(".user-dropdown-name");
      if (profileHeroName) {
        profileHeroName.textContent = result.profile.username;
      }
      if (userDropdownName) {
        userDropdownName.textContent = result.profile.username;
      }
      setAccountMessage(profileMessage, result.message, "success");
    } catch (error) {
      setAccountMessage(profileMessage, error.message, "error");
    }
  });
}

// 删除账号
if (deleteAccountForm) {
  const deleteAccountMessage = document.querySelector("#delete-account-message");

  deleteAccountForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const payload = {
      current_password: deleteAccountForm.elements.current_password.value,
    };

    try {
      setAccountMessage(deleteAccountMessage, "Deleting account...");
      const result = await postJson("/api/settings/delete-account", payload);
      deleteAccountForm.reset();
      setAccountMessage(deleteAccountMessage, result.message, "success");
      window.location.href = result.redirect || "/auth?mode=register";
    } catch (error) {
      setAccountMessage(deleteAccountMessage, error.message, "error");
    }
  });
}

// 上传个人头像
if (avatarInput) {
  const profileMessage = document.querySelector("#profile-message");

  avatarInput.addEventListener("change", async () => {
    const avatarFile = avatarInput.files?.[0];
    if (!avatarFile) {
      return;
    }

    const formData = new FormData();
    formData.append("avatar", avatarFile);

    try {
      setAccountMessage(profileMessage, "Uploading avatar...");
      const result = await postFormData("/api/profile/avatar", formData);
      updateAvatarUi(result.avatar_url);
      setAccountMessage(profileMessage, result.message, "success");
    } catch (error) {
      setAccountMessage(profileMessage, error.message, "error");
    } finally {
      avatarInput.value = "";
    }
  });
}

// 修改密码
if (changePasswordForm) {
  const settingsMessage = document.querySelector("#settings-message");

  changePasswordForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const payload = {
      current_password: changePasswordForm.elements.current_password.value,
      new_password: changePasswordForm.elements.new_password.value,
      confirm_new_password: changePasswordForm.elements.confirm_new_password.value,
    };

    const passwordError = validatePasswordPolicy(payload.new_password);
    if (passwordError) {
      setAccountMessage(settingsMessage, passwordError, "error");
      return;
    }

    try {
      setAccountMessage(settingsMessage, "Changing password...");
      const result = await postJson("/api/settings/change-password", payload);
      changePasswordForm.reset();
      setAccountMessage(settingsMessage, result.message, "success");
    } catch (error) {
      setAccountMessage(settingsMessage, error.message, "error");
    }
  });
}

const teamModal = document.querySelector("#team-modal");
const publicCampaignModal = document.querySelector("#public-campaign-modal");
const fundraiserAnalyticsModal = document.querySelector("#fundraiser-analytics-modal");
const impactDonationModal = document.querySelector("#impact-donation-modal");

// 打开团队成员简介弹窗
if (teamModal) {
  const modalName = document.querySelector("#team-modal-name");
  const modalNameZh = document.querySelector("#team-modal-name-zh");
  const modalRole = document.querySelector("#team-modal-role");
  const modalSummary = document.querySelector("#team-modal-summary");
  const modalPhotoImage = document.querySelector("#team-modal-photo-image");
  const memberCards = document.querySelectorAll(".team-member-card");
  const closeTriggers = teamModal.querySelectorAll("[data-close-modal='true']");

  const openModal = (card) => {
    modalName.textContent = card.dataset.memberName || "Member Name";
    modalNameZh.textContent = card.dataset.memberNameZh || "";
    modalRole.textContent = card.dataset.memberRole || "Role";
    modalSummary.textContent = card.dataset.memberSummary || "Member summary.";
    if (modalPhotoImage) {
      modalPhotoImage.src = card.dataset.memberPhoto || "";
      modalPhotoImage.alt = `${card.dataset.memberName || "Team member"} portrait`;
    }
    teamModal.removeAttribute("hidden");
    document.body.style.overflow = "hidden";
  };

  const closeModal = () => {
    teamModal.setAttribute("hidden", "");
    document.body.style.overflow = "";
  };

  memberCards.forEach((card) => {
    card.addEventListener("click", () => openModal(card));
  });

  closeTriggers.forEach((node) => {
    node.addEventListener("click", closeModal);
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && !teamModal.hasAttribute("hidden")) {
      closeModal();
    }
  });
}

// 打开公开筹款项目详情弹窗
if (publicCampaignModal) {
  const currentUserEmail = (document.body.dataset.currentUserEmail || "").trim().toLowerCase();
  const projectButtons = document.querySelectorAll(".public-campaign-open");
  const modalTitle = document.querySelector("#public-campaign-modal-title");
  const modalCategory = document.querySelector("#public-campaign-modal-category");
  const modalOwner = document.querySelector("#public-campaign-modal-owner");
  const modalGoal = document.querySelector("#public-campaign-modal-goal");
  const modalRaised = document.querySelector("#public-campaign-modal-raised");
  const modalProgress = document.querySelector("#public-campaign-modal-progress");
  const modalFundingStatus = document.querySelector("#public-campaign-modal-funding-status");
  const modalDeadlineStatus = document.querySelector("#public-campaign-modal-deadline-status");
  const modalPublished = document.querySelector("#public-campaign-modal-published");
  const modalDescription = document.querySelector("#public-campaign-modal-description");
  const modalImage = document.querySelector("#public-campaign-modal-image");
  const modalPlaceholder = document.querySelector("#public-campaign-modal-placeholder");
  const modalPrev = document.querySelector("#public-campaign-modal-prev");
  const modalNext = document.querySelector("#public-campaign-modal-next");
  const supportForm = document.querySelector("#public-campaign-support-form");
  const supportMessage = document.querySelector("#public-campaign-support-message");
  const favouriteForm = document.querySelector("#public-campaign-favourite-form");
  const favouriteButton = document.querySelector("#public-campaign-favourite-button");
  const supportConfirmModal = document.querySelector("#support-confirm-modal");
  const supportConfirmApproveButton = document.querySelector("#support-confirm-approve");
  const supportConfirmCancelButton = document.querySelector("#support-confirm-cancel");
  const supportConfirmCloseTriggers = supportConfirmModal?.querySelectorAll(
    "[data-close-support-confirm='true']"
  );
  const projectsFlashMessage = document.querySelector(".projects-flash");
  const closeTriggers = publicCampaignModal.querySelectorAll("[data-close-project-modal='true']");
  let currentProjectImages = [];
  let currentProjectImageIndex = 0;
  let activeProjectButton = null;
  let supportConfirmationApproved = false;

  const syncProjectModalQuery = (projectId = "") => {
    const currentUrl = new URL(window.location.href);
    if (projectId) {
      currentUrl.searchParams.set("campaign_id", String(projectId));
    } else {
      currentUrl.searchParams.delete("campaign_id");
    }
    window.history.replaceState({}, "", currentUrl.toString());
  };

  const renderProjectModalImage = () => {
    const imageUrl = currentProjectImages[currentProjectImageIndex] || "";

    if (modalImage && modalPlaceholder) {
      if (imageUrl) {
        modalImage.src = imageUrl;
        modalImage.hidden = false;
        modalPlaceholder.hidden = true;
      } else {
        modalImage.src = "";
        modalImage.hidden = true;
        modalPlaceholder.hidden = false;
      }
    }

    const showArrows = currentProjectImages.length > 1;
    if (modalPrev) {
      modalPrev.hidden = !showArrows;
    }
    if (modalNext) {
      modalNext.hidden = !showArrows;
    }
  };

  const openProjectModal = (button) => {
    activeProjectButton = button;
    supportConfirmationApproved = false;
    const ownerEmail = (button.dataset.projectOwnerEmail || "").trim().toLowerCase();
    const isOwnCampaign = Boolean(currentUserEmail && ownerEmail && currentUserEmail === ownerEmail);
    if (modalTitle) {
      modalTitle.textContent = button.dataset.projectTitle || "Campaign";
    }
    if (modalCategory) {
      modalCategory.textContent = button.dataset.projectCategory || "Other";
    }
    if (modalOwner) {
      modalOwner.textContent = button.dataset.projectOwner || "Unknown";
    }
    if (modalGoal) {
      modalGoal.textContent = button.dataset.projectGoal || "Goal pending";
    }
    if (modalRaised) {
      modalRaised.textContent = button.dataset.projectRaised || "$0 raised";
    }
    if (modalProgress) {
      modalProgress.textContent = button.dataset.projectProgress || "0%";
    }
    if (modalFundingStatus) {
      modalFundingStatus.textContent = button.dataset.projectFundingStatus || "Funding in progress";
    }
    if (modalDeadlineStatus) {
      modalDeadlineStatus.textContent = button.dataset.projectDeadlineStatus || "No deadline";
    }
    if (modalPublished) {
      modalPublished.textContent = button.dataset.projectPublished || "Ready for support";
    }
    if (modalDescription) {
      modalDescription.textContent =
        button.dataset.projectDescription || "This approved campaign is ready to receive support.";
    }

    try {
      const parsedImages = JSON.parse(button.dataset.projectImages || "[]");
      currentProjectImages = Array.isArray(parsedImages) ? parsedImages.filter(Boolean) : [];
    } catch (error) {
      currentProjectImages = [];
    }

    if (currentProjectImages.length === 0 && button.dataset.projectImage) {
      currentProjectImages = [button.dataset.projectImage];
    }
    currentProjectImageIndex = 0;
    renderProjectModalImage();

    if (favouriteForm && favouriteButton) {
      const projectId = button.dataset.projectId;
      const isFavourite = button.dataset.projectIsFavourite === "true";
      favouriteForm.action = isFavourite
        ? `/projects/${projectId}/favourites/remove`
        : `/projects/${projectId}/favourites/save`;
      favouriteButton.textContent = isFavourite
        ? "Remove from favourites"
        : "Save to favourites";
      favouriteButton.className = isFavourite ? "ghost-button" : "solid-button";
    }
    if (supportForm) {
      supportForm.action = `/projects/${button.dataset.projectId}/support`;
      supportForm.hidden = isOwnCampaign;
    }
    if (supportMessage) {
      if (isOwnCampaign) {
        setAccountMessage(
          supportMessage,
          "You cannot support your own campaign.",
          "error"
        );
      } else if (projectsFlashMessage?.textContent?.trim()) {
        setAccountMessage(
          supportMessage,
          projectsFlashMessage.textContent.trim(),
          projectsFlashMessage.classList.contains("error") ? "error" : "success"
        );
      } else {
        setAccountMessage(supportMessage, "");
      }
    }

    publicCampaignModal.removeAttribute("hidden");
    document.body.style.overflow = "hidden";
    syncProjectModalQuery(button.dataset.projectId || "");

    if (button.dataset.projectId) {
      fetch(`/api/projects/${button.dataset.projectId}/view`, {
        method: "POST",
      }).catch(() => {});
    }
  };

  const closeProjectModal = () => {
    publicCampaignModal.setAttribute("hidden", "");
    closeSupportConfirmModal();
    document.body.style.overflow = "";
    activeProjectButton = null;
    supportConfirmationApproved = false;
    syncProjectModalQuery();
  };

  const openSupportConfirmModal = () => {
    if (!supportConfirmModal) {
      return;
    }
    supportConfirmModal.removeAttribute("hidden");
  };

  const closeSupportConfirmModal = () => {
    if (!supportConfirmModal) {
      return;
    }
    supportConfirmModal.setAttribute("hidden", "");
  };

  projectButtons.forEach((button) => {
    button.addEventListener("click", () => openProjectModal(button));
  });

  closeTriggers.forEach((node) => {
    node.addEventListener("click", closeProjectModal);
  });

  supportConfirmCloseTriggers?.forEach((node) => {
    node.addEventListener("click", () => {
      supportConfirmationApproved = false;
      closeSupportConfirmModal();
    });
  });

  supportConfirmCancelButton?.addEventListener("click", () => {
    supportConfirmationApproved = false;
    closeSupportConfirmModal();
  });

  supportConfirmApproveButton?.addEventListener("click", () => {
    if (!supportForm) {
      return;
    }
    supportConfirmationApproved = true;
    closeSupportConfirmModal();
    supportForm.requestSubmit();
  });

  supportForm?.addEventListener("submit", (event) => {
    const amountInput = supportForm.elements.amount;
    const cleanAmount = Number(amountInput?.value || 0);

    if (!Number.isFinite(cleanAmount) || cleanAmount <= 1000 || supportConfirmationApproved) {
      supportConfirmationApproved = false;
      return;
    }

    event.preventDefault();
    openSupportConfirmModal();
  });

  modalPrev?.addEventListener("click", () => {
    if (currentProjectImages.length <= 1) {
      return;
    }
    currentProjectImageIndex =
      (currentProjectImageIndex - 1 + currentProjectImages.length) % currentProjectImages.length;
    renderProjectModalImage();
  });

  modalNext?.addEventListener("click", () => {
    if (currentProjectImages.length <= 1) {
      return;
    }
    currentProjectImageIndex =
      (currentProjectImageIndex + 1) % currentProjectImages.length;
    renderProjectModalImage();
  });

  document.addEventListener("keydown", (event) => {
    if (publicCampaignModal.hasAttribute("hidden")) {
      return;
    }

    if (event.key === "ArrowLeft" && currentProjectImages.length > 1) {
      currentProjectImageIndex =
        (currentProjectImageIndex - 1 + currentProjectImages.length) % currentProjectImages.length;
      renderProjectModalImage();
      return;
    }

    if (event.key === "ArrowRight" && currentProjectImages.length > 1) {
      currentProjectImageIndex =
        (currentProjectImageIndex + 1) % currentProjectImages.length;
      renderProjectModalImage();
      return;
    }

    if (event.key === "Escape") {
      if (supportConfirmModal && !supportConfirmModal.hasAttribute("hidden")) {
        supportConfirmationApproved = false;
        closeSupportConfirmModal();
        return;
      }
      closeProjectModal();
    }
  });

  const requestedCampaignId = new URLSearchParams(window.location.search).get("campaign_id");
  if (requestedCampaignId) {
    const targetButton = document.querySelector(
      `.public-campaign-open[data-project-id="${requestedCampaignId}"]`
    );
    if (targetButton) {
      openProjectModal(targetButton);
    }
  }
}

if (fundraiserAnalyticsModal) {
  const openButtons = document.querySelectorAll(".fundraiser-analytics-open");
  const closeTriggers = fundraiserAnalyticsModal.querySelectorAll("[data-close-fundraiser-analytics='true']");
  const modalTitle = document.querySelector("#fundraiser-analytics-title");
  const modalCategory = document.querySelector("#fundraiser-analytics-category");
  const modalStatus = document.querySelector("#fundraiser-analytics-status");
  const modalViews = document.querySelector("#fundraiser-analytics-views");
  const modalShortlists = document.querySelector("#fundraiser-analytics-shortlists");
  const modalRaised = document.querySelector("#fundraiser-analytics-raised");
  const modalGoal = document.querySelector("#fundraiser-analytics-goal");
  const modalProgress = document.querySelector("#fundraiser-analytics-progress");
  const modalFundingStatus = document.querySelector("#fundraiser-analytics-funding-status");
  const modalDeadlineStatus = document.querySelector("#fundraiser-analytics-deadline-status");
  const modalLatestViewed = document.querySelector("#fundraiser-analytics-latest-viewed");
  const modalLatestShortlisted = document.querySelector("#fundraiser-analytics-latest-shortlisted");
  const modalCreated = document.querySelector("#fundraiser-analytics-created");
  const modalUpdated = document.querySelector("#fundraiser-analytics-updated");
  const modalManageLink = document.querySelector("#fundraiser-analytics-manage-link");

  const closeModal = () => {
    fundraiserAnalyticsModal.setAttribute("hidden", "");
    document.body.style.overflow = "";
  };

  const openModal = (button) => {
    if (modalTitle) modalTitle.textContent = button.dataset.fundraiserTitle || "Campaign";
    if (modalCategory) modalCategory.textContent = button.dataset.fundraiserCategory || "Other";
    if (modalStatus) modalStatus.textContent = button.dataset.fundraiserStatus || "Draft";
    if (modalViews) modalViews.textContent = button.dataset.fundraiserViews || "0";
    if (modalShortlists) modalShortlists.textContent = button.dataset.fundraiserShortlists || "0";
    if (modalRaised) modalRaised.textContent = button.dataset.fundraiserRaised || "$0";
    if (modalGoal) modalGoal.textContent = button.dataset.fundraiserGoal || "Goal pending";
    if (modalProgress) modalProgress.textContent = button.dataset.fundraiserProgress || "0%";
    if (modalFundingStatus) {
      modalFundingStatus.textContent = button.dataset.fundraiserFundingStatus || "Funding in progress";
    }
    if (modalDeadlineStatus) {
      modalDeadlineStatus.textContent = button.dataset.fundraiserDeadlineStatus || "No deadline";
    }
    if (modalLatestViewed) {
      modalLatestViewed.textContent = button.dataset.fundraiserLatestViewed || "No views yet";
    }
    if (modalLatestShortlisted) {
      modalLatestShortlisted.textContent =
        button.dataset.fundraiserLatestShortlisted || "No shortlists yet";
    }
    if (modalCreated) modalCreated.textContent = button.dataset.fundraiserCreated || "";
    if (modalUpdated) modalUpdated.textContent = button.dataset.fundraiserUpdated || "";
    if (modalManageLink) {
      modalManageLink.href = button.dataset.fundraiserManageUrl || "/your-fundraisers";
    }

    fundraiserAnalyticsModal.removeAttribute("hidden");
    document.body.style.overflow = "hidden";
  };

  openButtons.forEach((button) => {
    button.addEventListener("click", () => openModal(button));
  });
  closeTriggers.forEach((node) => node.addEventListener("click", closeModal));

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && !fundraiserAnalyticsModal.hasAttribute("hidden")) {
      closeModal();
    }
  });
}

if (impactDonationModal) {
  const openButtons = document.querySelectorAll(".donation-history-open");
  const closeTriggers = impactDonationModal.querySelectorAll("[data-close-impact-donation='true']");
  const modalTitle = document.querySelector("#impact-donation-title");
  const modalCategory = document.querySelector("#impact-donation-category");
  const modalAmount = document.querySelector("#impact-donation-amount");
  const modalDate = document.querySelector("#impact-donation-date");
  const modalFundraiser = document.querySelector("#impact-donation-fundraiser");
  const modalRaised = document.querySelector("#impact-donation-raised");
  const modalGoal = document.querySelector("#impact-donation-goal");
  const modalProgress = document.querySelector("#impact-donation-progress");
  const modalFundingStatus = document.querySelector("#impact-donation-funding-status");
  const modalDeadlineStatus = document.querySelector("#impact-donation-deadline-status");
  const modalDetailLink = document.querySelector("#impact-donation-detail-link");

  const closeModal = () => {
    impactDonationModal.setAttribute("hidden", "");
    document.body.style.overflow = "";
  };

  const openModal = (button) => {
    if (modalTitle) modalTitle.textContent = button.dataset.donationTitle || "Donation";
    if (modalCategory) modalCategory.textContent = button.dataset.donationCategory || "Other";
    if (modalAmount) modalAmount.textContent = button.dataset.donationAmount || "$0";
    if (modalDate) modalDate.textContent = button.dataset.donationDate || "";
    if (modalFundraiser) modalFundraiser.textContent = button.dataset.donationFundraiser || "Unknown";
    if (modalRaised) modalRaised.textContent = button.dataset.donationRaised || "$0";
    if (modalGoal) modalGoal.textContent = button.dataset.donationGoal || "Goal pending";
    if (modalProgress) modalProgress.textContent = button.dataset.donationProgress || "0%";
    if (modalFundingStatus) {
      modalFundingStatus.textContent = button.dataset.donationFundingStatus || "Funding in progress";
    }
    if (modalDeadlineStatus) {
      modalDeadlineStatus.textContent = button.dataset.donationDeadlineStatus || "No deadline";
    }
    if (modalDetailLink) {
      modalDetailLink.href = button.dataset.donationDetailUrl || "/projects";
    }

    impactDonationModal.removeAttribute("hidden");
    document.body.style.overflow = "hidden";
  };

  openButtons.forEach((button) => {
    button.addEventListener("click", () => openModal(button));
  });
  closeTriggers.forEach((node) => node.addEventListener("click", closeModal));

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && !impactDonationModal.hasAttribute("hidden")) {
      closeModal();
    }
  });
}

// Your Impact 余额充值弹窗与模拟付款
if (impactRechargeModal) {
  const openButton = document.querySelector("#impact-recharge-open");
  const closeTriggers = impactRechargeModal.querySelectorAll("[data-close-impact-recharge='true']");
  const amountButtons = impactRechargeModal.querySelectorAll(".impact-amount-option");
  const customAmountInput = document.querySelector("#impact-custom-amount");
  const confirmAmountButton = document.querySelector("#impact-confirm-amount");
  const payStep = document.querySelector("#impact-recharge-step-pay");
  const selectedAmountNode = document.querySelector("#impact-selected-amount");
  const resultActions = document.querySelector("#impact-payment-result-actions");
  const successButton = document.querySelector("#impact-payment-success");
  const failureButton = document.querySelector("#impact-payment-failure");
  const rechargeMessage = document.querySelector("#impact-recharge-message");
  const balanceMessage = document.querySelector("#impact-balance-message");
  const balanceAmountNode = document.querySelector("#impact-balance-amount");
  let selectedAmount = 0;

  const resetRechargeState = () => {
    selectedAmount = 0;
    amountButtons.forEach((button) => button.classList.remove("is-active"));
    if (customAmountInput) {
      customAmountInput.value = "";
    }
    if (selectedAmountNode) {
      selectedAmountNode.textContent = formatUsdAmount(0);
    }
    if (payStep) {
      payStep.hidden = true;
    }
    setAccountMessage(rechargeMessage, "");
  };

  const openRechargeModal = () => {
    resetRechargeState();
    impactRechargeModal.removeAttribute("hidden");
    document.body.style.overflow = "hidden";
  };

  const closeRechargeModal = () => {
    impactRechargeModal.setAttribute("hidden", "");
    document.body.style.overflow = "";
    resetRechargeState();
  };

  const setSelectedAmount = (amount) => {
    selectedAmount = amount;
    amountButtons.forEach((button) => {
      button.classList.toggle("is-active", Number(button.dataset.amount) === amount);
    });
    if (selectedAmountNode) {
      selectedAmountNode.textContent = formatUsdAmount(amount);
    }
  };

  openButton?.addEventListener("click", openRechargeModal);
  closeTriggers.forEach((node) => node.addEventListener("click", closeRechargeModal));

  amountButtons.forEach((button) => {
    button.addEventListener("click", () => {
      if (customAmountInput) {
        customAmountInput.value = "";
      }
      setSelectedAmount(Number(button.dataset.amount || "0"));
    });
  });

  customAmountInput?.addEventListener("input", () => {
    amountButtons.forEach((button) => button.classList.remove("is-active"));
    const customValue = Number(customAmountInput.value);
    selectedAmount = Number.isFinite(customValue) ? customValue : 0;
    if (selectedAmountNode) {
      selectedAmountNode.textContent = formatUsdAmount(selectedAmount);
    }
  });

  confirmAmountButton?.addEventListener("click", () => {
    if (!selectedAmount || selectedAmount < 1) {
      setAccountMessage(
        rechargeMessage,
        "Please select or enter an amount of at least $1.",
        "error"
      );
      return;
    }
    if (payStep) {
      payStep.hidden = false;
    }
    setAccountMessage(
      rechargeMessage,
      "Amount confirmed. Scan the QR code, then choose Success or Failed.",
      "success"
    );
  });

  successButton?.addEventListener("click", async () => {
    try {
      setAccountMessage(rechargeMessage, "Applying recharge...");
      const result = await postJson("/api/impact/recharge", { amount: selectedAmount });
      if (balanceAmountNode) {
        balanceAmountNode.textContent = formatUsdAmount(result.balance);
      }
      setAccountMessage(balanceMessage, result.message, "success");
      closeRechargeModal();
    } catch (error) {
      setAccountMessage(rechargeMessage, error.message, "error");
    }
  });

  failureButton?.addEventListener("click", () => {
    setAccountMessage(rechargeMessage, "Recharge was not completed. You can try again.", "error");
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && !impactRechargeModal.hasAttribute("hidden")) {
      closeRechargeModal();
    }
  });
}

// 项目图片一次性多选提示
if (campaignImagesInput && campaignImagesSelectionStatus && campaignImagesFileLabel) {
  const defaultSelectionMessage = "No images selected yet.";
  const defaultFileLabel = "No files chosen";

  campaignImagesInput.addEventListener("invalid", () => {
    if (campaignImagesInput.validity.valueMissing) {
      campaignImagesInput.setCustomValidity("Please choose a file.");
      campaignImagesSelectionStatus.textContent = "Please choose a file.";
      campaignImagesSelectionStatus.style.color = "#c44949";
    } else {
      campaignImagesInput.setCustomValidity("");
    }
  });

  campaignImagesInput.addEventListener("change", () => {
    const fileCount = campaignImagesInput.files?.length || 0;
    campaignImagesInput.setCustomValidity("");

    if (fileCount === 0) {
      campaignImagesFileLabel.textContent = defaultFileLabel;
      campaignImagesSelectionStatus.textContent = defaultSelectionMessage;
      campaignImagesSelectionStatus.style.color = "";
      return;
    }

    campaignImagesFileLabel.textContent =
      fileCount === 1 ? "1 file chosen" : `${fileCount} files chosen`;

    if (fileCount > 5) {
      campaignImagesSelectionStatus.textContent =
        "Select up to 5 images in a single upload.";
      campaignImagesSelectionStatus.style.color = "#c44949";
      return;
    }

    const imageLabel = fileCount === 1 ? "image" : "images";
    campaignImagesSelectionStatus.textContent =
      `${fileCount} ${imageLabel} selected. They will be uploaded together.`;
    campaignImagesSelectionStatus.style.color = "";
  });
}

// 创建筹款项目页标题英文校验提示
if (campaignCreateDraftForm) {
  const campaignTitleInput = campaignCreateDraftForm.elements.title;

  if (campaignTitleInput) {
    campaignTitleInput.addEventListener("invalid", () => {
      if (campaignTitleInput.validity.valueMissing) {
        campaignTitleInput.setCustomValidity("Please fill out this field.");
      } else if (campaignTitleInput.validity.tooShort) {
        campaignTitleInput.setCustomValidity("Please lengthen this text to at least 4 characters.");
      } else {
        campaignTitleInput.setCustomValidity("");
      }
    });

    campaignTitleInput.addEventListener("input", () => {
      campaignTitleInput.setCustomValidity("");
    });
  }
}

// 项目工作流页必填字段英文校验提示
if (campaignBasicForm) {
  const basicTitleInput = campaignBasicForm.elements.title;

  if (basicTitleInput) {
    basicTitleInput.addEventListener("invalid", () => {
      if (basicTitleInput.validity.valueMissing) {
        basicTitleInput.setCustomValidity("Please fill out this field.");
      } else if (basicTitleInput.validity.tooShort) {
        basicTitleInput.setCustomValidity("Please lengthen this text to at least 4 characters.");
      } else {
        basicTitleInput.setCustomValidity("");
      }
    });

    basicTitleInput.addEventListener("input", () => {
      basicTitleInput.setCustomValidity("");
    });
  }
}

if (campaignGoalForm) {
  const goalAmountInput = campaignGoalForm.elements.goal_amount;

  if (goalAmountInput) {
    goalAmountInput.addEventListener("invalid", () => {
      if (goalAmountInput.validity.valueMissing) {
        goalAmountInput.setCustomValidity("Please enter the required amount.");
      } else if (goalAmountInput.validity.rangeUnderflow) {
        goalAmountInput.setCustomValidity("Please enter an amount greater than or equal to 1.");
      } else {
        goalAmountInput.setCustomValidity("");
      }
    });

    goalAmountInput.addEventListener("input", () => {
      goalAmountInput.setCustomValidity("");
    });
  }
}

if (campaignDescriptionForm) {
  const descriptionInput = campaignDescriptionForm.elements.description;

  if (descriptionInput) {
    descriptionInput.addEventListener("invalid", () => {
      if (descriptionInput.validity.valueMissing) {
        descriptionInput.setCustomValidity("Please fill out this field.");
      } else if (descriptionInput.validity.tooShort) {
        descriptionInput.setCustomValidity("Please lengthen this text to at least 20 characters.");
      } else {
        descriptionInput.setCustomValidity("");
      }
    });

    descriptionInput.addEventListener("input", () => {
      descriptionInput.setCustomValidity("");
    });
  }
}

if (campaignDeadlineForm) {
  const deadlineInput = campaignDeadlineForm.elements.deadline;

  if (deadlineInput) {
    deadlineInput.addEventListener("invalid", () => {
      if (deadlineInput.validity.valueMissing) {
        deadlineInput.setCustomValidity("Please fill out this field.");
      } else {
        deadlineInput.setCustomValidity("");
      }
    });

    deadlineInput.addEventListener("input", () => {
      deadlineInput.setCustomValidity("");
    });
  }
}
