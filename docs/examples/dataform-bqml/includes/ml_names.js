function modelIdentifier(value) {
  if (typeof value !== "string" ||
      !/^[a-z][a-z0-9-]*\.[A-Za-z_][A-Za-z0-9_]*\.[A-Za-z_][A-Za-z0-9_]*$/.test(value)) {
    throw new Error("model_path must be a project.dataset.model identifier");
  }
  return "`" + value + "`";
}

module.exports = { modelIdentifier };
