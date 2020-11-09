# Інструкція 

## Згенерувати документацію з `src/`
Спочатку імпортувати `src` в `conf.py`.

Після: 
```bash
sphinx-apicod -f -o ./source ./../src/
```

Додати `source/modules.rst` в *toctree* в `index.rst`

## Згенерувати html

```bash
make html
```

Якщо віндовс: 

```bash
sphinx-build -b html . _build
```