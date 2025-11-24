'use strict';

function wrapWebpackDevServerConfig(originalCreateDevServerConfig) {
  return function patchedCreateDevServerConfig(proxy, allowedHost) {
    const config = originalCreateDevServerConfig(proxy, allowedHost);

    const hasDeprecatedHooks =
      typeof config.onBeforeSetupMiddleware === 'function' ||
      typeof config.onAfterSetupMiddleware === 'function';

    if (!hasDeprecatedHooks) {
      return config;
    }

    const { onBeforeSetupMiddleware, onAfterSetupMiddleware } = config;

    config.setupMiddlewares = (middlewares, devServer) => {
      if (!devServer) {
        throw new Error('webpack-dev-server is not defined');
      }

      if (typeof onBeforeSetupMiddleware === 'function') {
        onBeforeSetupMiddleware(devServer);
      }

      if (typeof onAfterSetupMiddleware === 'function') {
        onAfterSetupMiddleware(devServer);
      }

      return middlewares;
    };

    delete config.onBeforeSetupMiddleware;
    delete config.onAfterSetupMiddleware;

    return config;
  };
}

module.exports = wrapWebpackDevServerConfig;