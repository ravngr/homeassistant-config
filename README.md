![GitHub](https://img.shields.io/github/license/ravngr/homeassistant-config) ![GitHub last commit (branch)](https://img.shields.io/github/last-commit/ravngr/homeassistant-config/main) ![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/ravngr/homeassistant-config/ci.yaml?label=CI)

# homeassistant-config
My [Home Assistant](https://home-assistant.io/) configuration. It is heavily inspired by the use of packages in [frenck/home-assistant-config](https://github.com/frenck/home-assistant-config), though I made my own spin on the structure. Other shared configurations have also provided inspiration, such as [CCOSTAN/Home-AssistantConfig](https://github.com/CCOSTAN/Home-AssistantConfig).

## Structure
- `config` Root for all Home Assistant configuration files.
- `config/configuration.yaml` The root YAML configuration file. Fairly minimal, imports packages and includes automations, scripts, and scenes from the config root. Some core `homeassistant` configuration options were also moved here.
- `config/packages` Integrations, entities, and other configuration artefacts are divided into packages based upon function.
- `config/packages/core` Core/internal Home Assistant services are split into their own sub-directory.
- `script` Some utility scripts for validation and testing.

## CI
Simple CI is implemented in a GitHub action based upon [frenck/action-home-assistant](https://github.com/frenck/action-home-assistant). My implementation is simpler and is compatible with [nektos/act](https://github.com/nektos/act), which has a slightly funny interpretation of the action workspace that makes it difficult to remove config files before running tests. The workflow workflow removes HACS medules before testing to avoid false-negatives.
