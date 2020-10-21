# Contributing Guide

- Покращити індекс досить просто. Цей документ окреслить як це можна зробити. 

## General
- [Codebase Structure](./CODEBASE_STRUCTURE.md) окреслює загальну структуру проєкту
- Зауваження щодо параметрів/якості даних можна залишити створивши `issue`.
- PR із запропонованими змінами до вихідного коду також вітаються: 

## Submitting changes

Як запропонувати зміни?

- Fork the repo
  - <https://github.com/hp0404/template/fork>
- Check out a new branch based and name it to what you intend to do:
  - Example:
    ````
    $ git checkout -b BRANCH_NAME
    ````
    If you get an error, you may need to fetch fooBar first by using
    ````
    $ git remote update && git fetch
    ````
  - Use one branch per fix / feature
- Commit your changes
  - Please provide a git message that explains what you've done
  - Please make sure your commits follow the [conventions](https://gist.github.com/robertpainsi/b632364184e70900af4ab688decf6f53#file-commit-message-guidelines-md)
  - Commit to the forked repository
  - Example:
    ````
    $ git commit -am 'Add some fooBar'
    ````
- Push to the branch
  - Example:
    ````
    $ git push origin BRANCH_NAME
    ````
- Make a pull request
  - Make sure you send the PR to the `fooBar` branch

