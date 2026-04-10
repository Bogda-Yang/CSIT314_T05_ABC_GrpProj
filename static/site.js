const userMenu = document.querySelector(".user-menu");
const profileForm = document.querySelector("#profile-form");
const changePasswordForm = document.querySelector("#change-password-form");
const deleteAccountForm = document.querySelector("#delete-account-form");
const avatarInput = document.querySelector("#avatar-input");
const profileAvatarFrame = document.querySelector("#profile-avatar-frame");
const profileAvatarImage = document.querySelector("#profile-avatar-image");
const homeUserAvatar = document.querySelector("#home-user-avatar");

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

const teamModal = document.querySelector("#team-modal");

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
