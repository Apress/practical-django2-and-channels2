const common = require('./webpack.config')

module.exports = {
  mode: 'production',
  entry: common.entry,
  plugins: common.plugins,
  output: {
    filename: '[name].bundle.js',
    path: common.output.path
  }
};
