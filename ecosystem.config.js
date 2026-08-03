module.exports = {
  apps: [
    {
      name: 'synk-orchestrator',
      script: '/Users/davidnows/synk-ia-orchestrator.js',
      instances: 1,
      exec_mode: 'fork',
      env: {
        NODE_ENV: 'production',
        CONFIG_PATH: '/Users/davidnows/synk-ia-global-config.yaml',
        ORCHESTRATOR_PORT: 9500
      },
      max_memory_restart: '500M',
      error_file: '/Users/davidnows/.synkia-ai-hub/logs/orchestrator-error.log',
      out_file: '/Users/davidnows/.synkia-ai-hub/logs/orchestrator-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
      autorestart: true,
      watch: false,
      ignore_watch: ['node_modules', '.git', 'logs'],
      merge_logs: true,
      max_restarts: 10,
      min_uptime: '10s'
    },
    {
      name: 'synk-model-selector',
      script: '/Users/davidnows/synk-ia-model-selector.js',
      instances: 1,
      exec_mode: 'fork',
      env: {
        NODE_ENV: 'production',
        CONFIG_PATH: '/Users/davidnows/synk-ia-global-config.yaml',
        MODEL_SELECTOR_PORT: 9501
      },
      max_memory_restart: '500M',
      error_file: '/Users/davidnows/.synkia-ai-hub/logs/model-selector-error.log',
      out_file: '/Users/davidnows/.synkia-ai-hub/logs/model-selector-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
      autorestart: true,
      watch: false,
      ignore_watch: ['node_modules', '.git', 'logs'],
      merge_logs: true,
      max_restarts: 10,
      min_uptime: '10s'
    }
  ]
};
