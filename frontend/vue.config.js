const { defineConfig } = require('@vue/cli-service')
const path = require('path');

module.exports = defineConfig({
  // 配置HTML模板和favicon
  pages: {
    index: {
      entry: 'src/main.js',
      template: 'public/index.html',
      filename: 'index.html',
      title: 'LeafAuto Web',
      chunks: ['chunk-vendors', 'chunk-common', 'index']
    }
  },
  transpileDependencies: true,
  configureWebpack: {
    resolve: {
      alias: {
        '@': path.resolve(__dirname, 'src'),
      },
    },
  },
  devServer: {
    port: 8080,
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true,
        pathRewrite: {
          '^/api': '/api'
        }
      }
    },
    client: {
      overlay: {
        runtimeErrors: (error) => {
          const ignoreErrors = [
            'ResizeObserver loop completed with undelivered notifications',
            'ResizeObserver loop limit exceeded'
          ]
          if (ignoreErrors.some(ignoreError => error.message.includes(ignoreError))) {
            return false
          }
          return true
        }
      }
    }
  },
  // 解决特性标志警告
  chainWebpack: config => {
    config.plugin('define').tap(args => {
      args[0]['__VUE_PROD_HYDRATION_MISMATCH_DETAILS__'] = JSON.stringify(false)
      return args
    })
  }
})