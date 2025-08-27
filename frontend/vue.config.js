module.exports = {
  // 解决 MIME 类型和字符编码问题
  devServer: {
    headers: {
      "Content-Type": "text/html; charset=utf-8"
    }
  },

  // 解决 Vue 特性标志警告
  chainWebpack: config => {
    config.plugin('define').tap(definitions => {
      Object.assign(definitions[0], {
        __VUE_PROD_HYDRATION_MISMATCH_DETAILS__: 'false',
        __VUE_PROD_DEVTOOLS__: 'false'
      });
      return definitions;
    });

    // 设置 HTML 文件字符编码和标题
    config.plugin('html').tap(args => {
      args[0].title = "城市餐饮店铺选址分析系统";
      args[0].meta = {
        charset: { charset: 'utf-8' },
        viewport: 'width=device-width, initial-scale=1.0'
      };
      return args;
    });

    // 禁用预取和预加载以减少警告
    config.plugins.delete('prefetch');
    config.plugins.delete('preload');
  },

  // 设置公共路径
  publicPath: process.env.NODE_ENV === 'production' ? '/' : '/',

  // 配置分块策略
  configureWebpack: {
    optimization: {
      splitChunks: {
        chunks: 'all',
        minSize: 20000,
        maxSize: 250000,
        minChunks: 1,
        maxAsyncRequests: 30,
        maxInitialRequests: 30,
        automaticNameDelimiter: '~',
        cacheGroups: {
          leaflet: {
            test: /[\\/]node_modules[\\/]leaflet[\\/]/,
            name: 'chunk-leaflet',
            priority: 20
          },
          vue: {
            test: /[\\/]node_modules[\\/](vue|vue-router)[\\/]/,
            name: 'chunk-vue',
            priority: 10
          },
          default: {
            minChunks: 2,
            priority: -20,
            reuseExistingChunk: true
          }
        }
      }
    },
    // 关闭性能提示
    performance: {
      hints: false
    }
  }
};