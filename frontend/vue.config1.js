module.exports = {
  // 解决 MIME 类型和字符编码问题
  configureWebpack: {
    devServer: {
      headers: {
        "Content-Type": "text/html; charset=utf-8"
      }
    }
  },
  
  // 解决 Vue 特性标志警告
  chainWebpack: config => {
    config.plugin('define').tap(definitions => {
      Object.assign(definitions[0], {
        __VUE_PROD_HYDRATION_MISMATCH_DETAILS__: 'false'
      });
      return definitions;
    });
    
    // 设置 HTML 文件字符编码
    config.plugin('html').tap(args => {
      args[0].title = "城市餐饮店铺选址分析系统";
      args[0].meta = {
        charset: { charset: 'utf-8' },
        viewport: 'width=device-width, initial-scale=1.0'
      };
      return args;
    });
  },
  
  // 设置公共路径
  publicPath: process.env.NODE_ENV === 'production' ? '/' : '/'
};