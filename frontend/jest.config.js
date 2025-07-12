module.exports = {
  preset: '@vue/cli-plugin-unit-jest/presets/default',
  transform: {
    '^.+\\.vue$': '@vue/vue3-jest',
    '^.+\\.js$': 'babel-jest',
  },
  // Module file extensions for importing
  moduleFileExtensions: ['js', 'json', 'vue'],
  // A map from regular expressions to module names that allow to stub out resources with a single module
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/src/$1',
  },
  // The test environment that will be used for testing
  testEnvironment: 'jsdom',
  // A list of paths to directories that Jest should use to search for files in
  roots: [
    '<rootDir>/src',
    '<rootDir>/tests/unit' // A separate directory for tests
  ],
};
