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
      let section = dragged.closest("details")?.dataset.section
      let slot = event.target.closest(".slot");

      if (slot && section && slot.dataset.section !== "free" && slot.dataset.section !== section) {
        slot = null
      }

      if (slot == null) {
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
        copy.dataset.filledSection = slot.dataset.section
        copy.dataset.filledLabel = slot.dataset.label
        copy.dataset.filledHours = courseHours

      } else if (slot != null) {
        slot.replaceWith(copy);
        copy.replacedSlot = slot;
        copy.dataset.filledSection = slot.dataset.section
        copy.dataset.filledLabel = slot.dataset.label
        copy.dataset.filledHours = slotHours

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
  let data = collectPlan()

  document.querySelector('[name="plan"]').value = data.plan.map(s => s.join(",")).join("\n")
  document.querySelector('[name="slot_hours"]').value = data.slotHours.join(",")
});

function savePlan() {
  if (document.querySelector(".semester") == null) {
    return
  }

  let major = Array.from(document.querySelectorAll('select[name="major"]')).map((s) => s.value)
  let minor = Array.from(document.querySelectorAll('select[name="minor"]')).map((s) => s.value)
  let prior = document.querySelector('[name="prior"]').value
  let honors = document.querySelector('input[name="hnrs"]').checked
  let mode = document.querySelector('#plan-mode').value
  let semesters = Array.from(document.querySelectorAll(".semester")).map((s) => s.innerHTML)

  let lsuPlan = { majors: major, minors: minor, prior: prior, honors: honors, mode: mode, semesters: semesters }

  localStorage.setItem("lsuPlan", JSON.stringify(lsuPlan))
}

function restorePlan() {
  let saved = localStorage.getItem("lsuPlan")

  if (saved == null) {
    return
  }

  saved = JSON.parse(saved)

  if (document.querySelector(".semester") == null) {
    let majorSelects = document.querySelectorAll('select[name="major"]')

    for (let i = 0; i < majorSelects.length; i++) {
      majorSelects[i].value = saved.majors[i]
    }

    let minorSelects = document.querySelectorAll('select[name="minor"]')

    for (let i = 0; i < minorSelects.length; i++) {
      minorSelects[i].value = saved.minors[i]
    }

    document.querySelector('[name="prior"]').value = saved.prior
    document.querySelector('input[name="hnrs"]').checked = saved.honors

    updateHonorsBox();

    sessionStorage.setItem("restoring", "1")

    document.querySelector(`button[value="${saved.mode}"]`).click()

    return
  }

  if (sessionStorage.getItem("restoring") != null) {
    sessionStorage.removeItem("restoring")

    let boxes = document.querySelectorAll(".semester")

    if (boxes.length != saved.semesters.length) {
      return
    }

    for (let i = 0; i < boxes.length; i++) {
      boxes[i].innerHTML = saved.semesters[i]
    }

    document.querySelectorAll(".semester .chip[data-code]").forEach((chip) => {
      document.querySelectorAll(`.palette .chip[data-code="${chip.dataset.code}"]`).forEach((p) => {
        if (!p.classList.contains("repeatable")) {
          p.classList.add("used")
        }
      })
    })

    updateHours();
  }
}

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
  checkPrereqs();
  savePlan();
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
  } else if (dragged.dataset.filledSection) {
    let box = dragged.closest(".semester")
    let existing = box.querySelector(`.slot[data-section="${dragged.dataset.filledSection}"]`)

    if (existing) {
      existing.dataset.hours = Number(existing.dataset.hours) + Number(dragged.dataset.filledHours)
      dragged.remove()
    } else {
      let newSlot = document.createElement("div")
      newSlot.className = "chip slot"
      newSlot.draggable = true
      newSlot.dataset.section = dragged.dataset.filledSection
      newSlot.dataset.label = dragged.dataset.filledLabel
      newSlot.dataset.hours = dragged.dataset.filledHours
      newSlot.textContent = dragged.dataset.filledLabel
      dragged.replaceWith(newSlot)
    }
  } else {
    dragged.remove();
  }

  let codes = [dragged.dataset.code]

  let pieces = (dragged.dataset.options || "").split(",")

  for (const piece of pieces) {
    if (piece == "") {
      continue
    }

    codes.push(piece)
  }

  for (const code of codes) {
    if (document.querySelector(`.semester .chip[data-code="${code}"]`) == null) {
      document
        .querySelectorAll(`.palette .chip[data-code="${code}"]`)
        .forEach((chip) => {
          chip.classList.remove("used");
        });
    }
  }

  updateHours();
});

function applySearch() {
  let q = document.getElementById("search").value.trim().toLowerCase()
  document.querySelectorAll(".palette .chip").forEach((chip) => {
    let text = `${chip.dataset.code} ${chip.dataset.tip}`.toLowerCase()
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
}

document.getElementById("search").addEventListener("input", (event) => {
  let q = document.getElementById("search").value.trim().toLowerCase()
  applySearch();
  if (q.length >= 2) {
    fetch(`/elective_search?q=${encodeURIComponent(q)}`).then(r => r.json()).then(list => {
      if (document.getElementById("search").value.trim().toLowerCase() != q) {
        return
      }

      for (let subject of list) {
        let box = document.querySelector(`details[data-subject="${subject}"]`)

        if (!box) {
          continue
        }

        box.style.display = ""
        box.open = true
        box.closest("details:not([data-subject])").style.display = ""
        box.closest("details:not([data-subject])").open = true
      }
    })

  }
})

document.addEventListener("click", (event) => {
  let option = event.target.closest(".choice-option")

  if (option != null) {
    let chip = option.closest(".chip")
    let oldCode = chip.dataset.code
    let newCode = option.dataset.code
    let oldTip = chip.dataset.tip
    let oldHonors = oldTip.startsWith("HONORS: ")
    let newHonors = option.dataset.tip.startsWith("HONORS: ")
    let paletteChip = document.querySelector(`.palette .chip[data-code="${newCode}"]`)

    if (oldCode == newCode) {
      chip.querySelector(".choice-menu").hidden = true
      return
    }

    let inPlan = document.querySelector(`.semester .chip[data-code="${newCode}"]`)

    if (inPlan != null) {
      alert("Already in your plan!")
      return
    }

    chip.dataset.code = newCode

    if (document.querySelector(`.semester .chip[data-code="${oldCode}"]`) == null) {
      document
        .querySelectorAll(`.palette .chip[data-code="${oldCode}"]`)
        .forEach((chip) => {
          chip.classList.remove("used");
        });
    }

    chip.querySelector(".code-text").textContent = newCode;
    chip.querySelector(".warn-mark")?.remove()
    chip.classList.remove("missing")
    chip.dataset.tip = option.dataset.tip

    if (paletteChip != null) {
      chip.dataset.hours = paletteChip.dataset.hours
    }

    document
      .querySelectorAll(`.palette .chip[data-code="${newCode}"]`).forEach((p) => {
        p.classList.add("used");
      });

    if (newHonors && !oldHonors) {
      let flaggedChip = document.querySelector(`.semester .chip[data-hnrs-extra]`)

      if (flaggedChip) {
        chip.dataset.droppedExtra = flaggedChip.outerHTML

        let boxes = Array.from(document.querySelectorAll(".semester"))
        chip.dataset.droppedBox = boxes.indexOf(flaggedChip.closest(".semester"))

        flaggedChip.remove()

        document
          .querySelectorAll(`.palette .chip[data-code="${flaggedChip.dataset.code}"]`)
          .forEach((chip) => {
            chip.classList.remove("used");
          });

      }
    } else if (oldHonors && !newHonors && chip.dataset.droppedExtra) {
      let box = document.querySelectorAll(".semester")[Number(chip.dataset.droppedBox)]
      box.insertAdjacentHTML("beforeend", chip.dataset.droppedExtra)

      document
        .querySelectorAll(`.palette .chip[data-code="${box.lastElementChild.dataset.code}"]`).forEach((p) => {
          p.classList.add("used");
        });

      delete chip.dataset.droppedExtra
      delete chip.dataset.droppedBox
    }

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

function updateHonorsBox() {
  let hnrsLabel = document.getElementById("hnrs-label");
  let minorDropdown = document.querySelectorAll('select[name="minor"]');

  let found = false

  for (let select of minorDropdown) {
    if (select.selectedOptions[0].dataset.honors) {
      found = true
    }
  }

  hnrsLabel.hidden = !found
}

updateHonorsBox();

for (let select of document.querySelectorAll('select[name="minor"]')) {
  select.addEventListener("change", updateHonorsBox)
}

document.addEventListener("mouseover", (event) => {
  let toolTip = document.getElementById("tooltip")
  let target = event.target.closest(".choice-option[data-tip], .chip[data-tip]")

  if (!target || !target.dataset.tip) {
    return
  }

  if (event.target.closest(".note-mark")) {
    toolTip.hidden = true
    return
  }

  toolTip.textContent = target.dataset.tip
  toolTip.hidden = false
})

document.addEventListener("mouseout", (event) => {
  let toolTip = document.getElementById("tooltip")
  let target = event.target.closest(".choice-option[data-tip], .chip[data-tip]")

  if (!target || !target.dataset.tip) {
    return
  }

  if (event.relatedTarget?.closest(".chip, .choice-option") === target) {
    return
  }

  toolTip.hidden = true
})

document.addEventListener("mousemove", (event) => {
  let toolTip = document.getElementById("tooltip")

  if (toolTip.hidden) {
    return
  }


  toolTip.style.left = `${event.clientX + 12}px`
  if (event.clientX + 12 + toolTip.offsetWidth > window.innerWidth) {
    toolTip.style.left = `${event.clientX - toolTip.offsetWidth - 12}px`
  }
  toolTip.style.top = `${event.clientY + 12}px`
})

document.querySelectorAll("details[data-subject]").forEach((details) => {
  details.addEventListener("toggle", (event) => {
    if (!details.open || details.dataset.loaded) {
      return
    }

    details.dataset.loaded = "1"

    fetch(`/electives/${details.dataset.subject}`).then(r => r.json()).then(list => {
      for (let course of list) {
        let div = document.createElement("div")
        div.className = "chip"
        div.draggable = true
        div.dataset.code = course.code
        div.dataset.hours = course.hours
        div.dataset.tip = course.tip
        div.innerHTML = `${div.dataset.code} <span class="chip-title">${course.title}</span>`

        if (course.repeatable) {
          div.classList.add("repeatable")
        } else if (document.querySelector(`.semester .chip[data-code="${course.code}"]`)) {
          div.classList.add("used")
        }

        details.appendChild(div)
      }

      if (document.getElementById("search").value.trim() !== "") {
        applySearch()
      }
    })
  })
})

document.addEventListener("dragend", (event) => {
  dragged = null
})

function collectPlan() {
  let plan = [];
  let slotHours = [];

  document.querySelectorAll(".semester").forEach((box) => {
    let chips = box.querySelectorAll(".chip[data-code]");
    let codes = Array.from(chips).map((chip) => chip.dataset.code);

    let sum = 0
    box.querySelectorAll(".chip.slot").forEach((thing) => {
      sum += Number(thing.dataset.hours || 0)
    })

    slotHours.push(sum);
    plan.push(codes)

  });

  return { plan: plan, slotHours: slotHours }
}

let checkCount = 0

function checkPrereqs() {
  checkCount++;

  let mine = checkCount
  let data = collectPlan()

  let priorBox = document.querySelector('[name="prior"]').value
  fetch("/check_plan", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ plan: data.plan, prior: priorBox, slot_hours: data.slotHours }) }).then(r => r.json()).then(problems => {
    if (mine !== checkCount) {
      return
    }

    document.querySelectorAll(".semester .unknown-mark").forEach((mark => mark.remove()))

    document.querySelectorAll(".semester .chip.missing").forEach((chip) => {
      chip.classList.remove("missing")
      chip.querySelectorAll(".warn-mark").forEach(m => m.remove())
    })

    for (let p of problems) {
      let box = document.querySelectorAll(".semester")[p.semester - 1]
      let newChip = box.querySelector(`.chip[data-code="${p.code}"]`)

      if (!newChip) {
        continue
      }

      if (p.kind == "unknown") {
        let span = document.createElement("span")
        span.className = "note-mark unknown-mark"
        span.textContent = "?";
        span.dataset.note = p.message;

        (newChip.querySelector(".code") || newChip).appendChild(span)

      } else {
        newChip.classList.add("missing")

        let mark = document.createElement("span")
        mark.className = "note-mark warn-mark"
        mark.dataset.note = p.message
        mark.textContent = "⚠";

        (newChip.querySelector(".code") || newChip).appendChild(mark)
      }
    }

  })

}

document.getElementById("clear-plan")?.addEventListener("click", (event) => {
  if (!confirm("Clear your saved plan?")) {
    return
  }

  localStorage.removeItem("lsuPlan")
  window.location = "/"
})

restorePlan();
checkPrereqs();
savePlan();

document.querySelector('[name="prior"]').addEventListener("input", (event) => {
  checkPrereqs();
  savePlan();
})