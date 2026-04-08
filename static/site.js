const userMenu = document.querySelector(".user-menu");
const profileForm = document.querySelector("#profile-form");
const changePasswordForm = document.querySelector("#change-password-form");
const deleteAccountForm = document.querySelector("#delete-account-form");

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

// 更新个人信息
if (profileForm) {
  const profileMessage = document.querySelector("#profile-message");

  profileForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const payload = {
      username: profileForm.elements.username.value.trim(),
      contact_details: profileForm.elements.contact_details.value.trim(),
    };

    try {
      setAccountMessage(profileMessage, "Saving profile...");
      const result = await postJson("/api/profile/update", payload);
      profileForm.elements.username.value = result.profile.username;
      profileForm.elements.contact_details.value = result.profile.contact_details;
      setAccountMessage(profileMessage, result.message, "success");
    } catch (error) {
      setAccountMessage(profileMessage, error.message, "error");
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
