import test from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { openAndFocusCapReviewTarget } from "../app/lib/cap-review-input.mjs";
import { blockerFocusTarget } from "../app/lib/cap-workflow-view.mjs";

function fakeField(id, details) {
  return {
    id,
    focused: false,
    scrolled: false,
    closest(selector) {
      return selector === "details" ? details : null;
    },
    scrollIntoView() {
      this.scrolled = true;
    },
    focus() {
      this.focused = true;
      this.ownerDocument.activeElement = this;
    },
  };
}

function fakeRequiredInputsDom({ open = false } = {}) {
  const details = { open, tagName: "DETAILS", summary: "Required CAP inputs" };
  const field = fakeField("cap-field-product_mapping", details);
  const panel = { id: "cap-planning-panel" };
  const document = {
    activeElement: panel,
    getElementById(id) {
      if (id === field.id) return field;
      if (id === panel.id) return panel;
      return null;
    },
  };
  field.ownerDocument = document;
  return { document, field, details, panel };
}

test("product-mapping blocker still maps to the existing field id", () => {
  assert.equal(blockerFocusTarget("product_mapping"), "cap-field-product_mapping");
});

test("product-mapping review opens Required CAP inputs then focuses the field", () => {
  const { document, field, details, panel } = fakeRequiredInputsDom({ open: false });
  const scheduled = [];
  const found = openAndFocusCapReviewTarget(document, "cap-field-product_mapping", (fn) => scheduled.push(fn));
  assert.equal(found, true);
  assert.equal(details.open, true);
  assert.equal(field.focused, false);
  assert.equal(document.activeElement, panel);
  assert.equal(scheduled.length, 1);
  scheduled[0]();
  assert.equal(field.scrolled, true);
  assert.equal(field.focused, true);
  assert.equal(document.activeElement, field);
  assert.equal(document.activeElement.id, "cap-field-product_mapping");
});

test("already-open details can focus immediately without a second wait", () => {
  const { document, field, details } = fakeRequiredInputsDom({ open: true });
  const scheduled = [];
  openAndFocusCapReviewTarget(document, "cap-field-product_mapping", (fn) => scheduled.push(fn));
  assert.equal(details.open, true);
  assert.equal(scheduled.length, 0);
  assert.equal(field.focused, true);
  assert.equal(document.activeElement, field);
});

test("workspace reviewCapInput opens owning details before focusing", async () => {
  const workspace = await readFile(new URL("../app/components/EngineeringWorkspace.tsx", import.meta.url), "utf8");
  const panel = await readFile(new URL("../app/components/CapPlanningPanel.tsx", import.meta.url), "utf8");
  const reviewFn = workspace.match(/function reviewCapInput\(elementId: string\) \{[\s\S]*?\n {2}\}/)?.[0] ?? "";
  assert.match(workspace, /openAndFocusCapReviewTarget/);
  assert.match(reviewFn, /openAndFocusCapReviewTarget\(document, elementId\)/);
  assert.doesNotMatch(reviewFn, /capOperationEnabled/);
  assert.match(panel, /blockerFocusTarget\(key\)/);
  assert.match(panel, /onReviewInput\(target\)/);
});
