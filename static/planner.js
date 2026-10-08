let dragged = null;

document.addEventListener("dragstart", (event) => {
  dragged = event.target;
});

document.querySelectorAll(".semester").forEach((box) => {
  box.addEventListener("dragover", (event) => {
    event.preventDefault();
  });
  box.addEventListener("drop", (event) => {
    event.preventDefault();
    if (!dragged) {
      return
    } else if (!dragged.dataset.code && !dragged.classList.contains("slot")) {
      return;
    }

    if (dragged.closest(".palette") != null) {
      if (dragged.classList.contains("used")) {
        return;
      }

      let copy = dragged.cloneNode(true);
      let slot = event.target.closest(".slot");

      if (slot == null) {
        let section = dragged.closest("details").dataset.section;
        slot = box.querySelector(`.slot[data-section="${section}"]`);
      }

      if (slot == null) {
        slot = box.querySelector('.slot[data-section="free"]')
      }

      let courseHours = Number(copy.dataset.hours || 0)
      let slotHours = Number(slot?.dataset.hours || 0)

      if (slot != null && courseHours < slotHours) {
        slot.before(copy);
        slot.dataset.hours = slotHours - courseHours
        copy.shrunkSlot = slot;
      } else if (slot != null) {
        slot.replaceWith(copy);
        copy.replacedSlot = slot;
      } else {
        box.appendChild(copy);
      }

      document
        .querySelectorAll(`.palette .chip[data-code="${dragged.dataset.code}"]`)
        .forEach((chip) => {
          if (!chip.classList.contains("repeatable")) {
            chip.classList.add("used");
          }
        });
    } else {
      box.appendChild(dragged);
    }

    updateHours();
  });
});

document.querySelector("form").addEventListener("submit", (event) => {
  let lines = [];

  document.querySelectorAll(".semester").forEach((box) => {
    let chips = box.querySelectorAll(".chip[data-code]");
    let codes = Array.from(chips).map((chip) => chip.dataset.code);

    lines.push(codes.join(","));
  });

  document.querySelector('[name="plan"]').value = lines.join("\n");
});

function updateHours() {
  let total = 0;

  document.querySelectorAll(".semester").forEach((box) => {
    let sum = 0;

    box.querySelectorAll(".chip").forEach((chip) => {
      sum += Number(chip.dataset.hours || 0);
    });

    let span = box.querySelector("h3 span");

    span.textContent = `${sum} hrs`;
    span.classList.remove("over", "under");

    if (sum > 19) {
      span.classList.add("over");
    } else if (sum < 12) {
      span.classList.add("under");
    }

    total += sum;
  });

  document.getElementById("total_hours").textContent = total;
}

function closeMenus() {
  document.querySelectorAll(".choice-menu").forEach((menu) => {
    menu.hidden = true
  })
}

let palette = document.querySelector(".palette");

palette.addEventListener("dragover", (event) => {
  event.preventDefault();
});

palette.addEventListener("drop", (event) => {
  event.preventDefault();

  if (!dragged) {
    return;
  } else if (dragged.closest(".semester") == null) {
    return;
  } else if (dragged.classList.contains("slot")) {
    return;
  }

  if (dragged.shrunkSlot) {
    let s = dragged.shrunkSlot;

    s.dataset.hours = Number(s.dataset.hours) + Number(dragged.dataset.hours || 0)

    dragged.remove();
  } else if (dragged.replacedSlot) {
    dragged.replaceWith(dragged.replacedSlot);
  } else {
    dragged.remove();
  }

  document
    .querySelectorAll(`.palette .chip[data-code="${dragged.dataset.code}"]`)
    .forEach((chip) => {
      chip.classList.remove("used");
    });

  updateHours();
});

document.getElementById("search").addEventListener("input", (event) => {
  let q = event.target.value.trim().toLowerCase()

  document.querySelectorAll(".palette .chip").forEach((chip) => {
    let text = `${chip.dataset.code} ${chip.title}`.toLowerCase()
    chip.style.display = text.includes(q) ? "" : "none"
  })

  document.querySelectorAll(".palette details").forEach((section) => {
    let hasMatch = Array.from(section.querySelectorAll(".chip")).some((chip) => chip.style.display !== "none")

    if (!q) {
      section.style.display = ""
      section.open = false
    } else {
      section.style.display = hasMatch ? "" : "none"
      section.open = hasMatch
    }
  })
})

document.addEventListener("click", (event) => {
  let option = event.target.closest(".choice-option")

  if (option != null) {
    let chip = option.closest(".chip")
    let oldCode = chip.dataset.code
    let newCode = option.dataset.code
    let paletteChip = document.querySelector(`.palette .chip[data-code="${newCode}"]`)

    if (oldCode == newCode) {
      chip.querySelector(".choice-menu").hidden = true
      return
    }

    if (paletteChip != null && paletteChip.classList.contains("used")) {
      alert("Already in your plan!")
      return
    }

    chip.dataset.code = newCode
    chip.querySelector(".code").textContent = newCode;

    if (paletteChip != null) {
      chip.dataset.hours = paletteChip.dataset.hours
      chip.title = paletteChip.title
    }

    document
      .querySelectorAll(`.palette .chip[data-code="${oldCode}"]`)
      .forEach((c) => {
        c.classList.remove("used");
      });

    document
      .querySelectorAll(`.palette .chip[data-code="${newCode}"]`).forEach((p) => {
        p.classList.add("used");
      });

    chip.querySelector(".choice-menu").hidden = true

    updateHours();
    return
  }
  let choiceChip = event.target.closest(".choice")

  if (choiceChip != null) {
    let menu = choiceChip.querySelector(".choice-menu")
    let wasHidden = menu.hidden

    closeMenus()
    menu.hidden = !wasHidden
    return
  }

  closeMenus()
})
