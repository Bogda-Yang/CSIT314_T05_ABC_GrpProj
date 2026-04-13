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
  const projectButtons = document.querySelectorAll(".public-campaign-open");
  const modalTitle = document.querySelector("#public-campaign-modal-title");
  const modalCategory = document.querySelector("#public-campaign-modal-category");
  const modalOwner = document.querySelector("#public-campaign-modal-owner");
  const modalGoal = document.querySelector("#public-campaign-modal-goal");
  const modalDeadline = document.querySelector("#public-campaign-modal-deadline");
  const modalPublished = document.querySelector("#public-campaign-modal-published");
  const modalDescription = document.querySelector("#public-campaign-modal-description");
  const modalImage = document.querySelector("#public-campaign-modal-image");
  const modalPlaceholder = document.querySelector("#public-campaign-modal-placeholder");
  const modalPrev = document.querySelector("#public-campaign-modal-prev");
  const modalNext = document.querySelector("#public-campaign-modal-next");
  const closeTriggers = publicCampaignModal.querySelectorAll("[data-close-project-modal='true']");
  let currentProjectImages = [];
  let currentProjectImageIndex = 0;

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
    if (modalDeadline) {
      modalDeadline.textContent = button.dataset.projectDeadline || "No deadline published";
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

    publicCampaignModal.removeAttribute("hidden");
    document.body.style.overflow = "hidden";
  };

  const closeProjectModal = () => {
    publicCampaignModal.setAttribute("hidden", "");
    document.body.style.overflow = "";
  };

  projectButtons.forEach((button) => {
    button.addEventListener("click", () => openProjectModal(button));
  });

  closeTriggers.forEach((node) => {
    node.addEventListener("click", closeProjectModal);
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
      closeProjectModal();
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
