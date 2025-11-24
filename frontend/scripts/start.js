'use strict';

const devServerConfigPath = require.resolve('react-scripts/config/webpackDevServer.config');
const wrapWebpackDevServerConfig = require('./webpackDevServerConfigOverride');

const originalCreateDevServerConfig = require(devServerConfigPath);
const patchedCreateDevServerConfig = wrapWebpackDevServerConfig(originalCreateDevServerConfig);

require.cache[devServerConfigPath].exports = patchedCreateDevServerConfig;

require('react-scripts/scripts/start');