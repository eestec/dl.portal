# For now it is assumed that the developer runs this before committing
cp ../css/base.css backup_base.css && lessc style.less --yui-compress >../css/base.css
