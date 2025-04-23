import { IDomEditor, IToolbarConfig, IEditorConfig, IButtonMenu } from '@wangeditor/editor'

// 声明自定义菜单类型
class InsertTravelRouteMenu implements IButtonMenu {
  constructor() {
    this.title = '添加旅游路线'
    this.tag = 'button'
    this.iconSvg = '<svg viewBox="0 0 1024 1024"><path d="M512 85.333333c-164.949333 0-298.666667 133.738667-298.666667 298.666667 0 164.949333 298.666667 554.666667 298.666667 554.666667s298.666667-389.717333 298.666667-554.666667c0-164.928-133.717333-298.666667-298.666667-298.666667z m0 448a149.333333 149.333333 0 1 1 0-298.666666 149.333333 149.333333 0 0 1 0 298.666666z" fill="#1296db"></path></svg>'
  }

  // 菜单标题
  title: string
  // 菜单标签
  tag: string
  // 菜单图标
  iconSvg: string

  // 菜单是否激活
  isActive(editor: IDomEditor): boolean {
    return false
  }

  // 菜单是否禁用
  isDisabled(editor: IDomEditor): boolean {
    return false
  }

  // 菜单执行命令
  exec(editor: IDomEditor, value: string | boolean) {
    if (editor.getMenuConfig('insertTravelRoute')) {
      const { openMapDialog } = editor.getMenuConfig('insertTravelRoute')
      if (typeof openMapDialog === 'function') {
        openMapDialog()
      }
    }
  }

  // 获取值
  getValue(editor: IDomEditor): string | boolean {
    return ''
  }
}

// 定义菜单配置
export const insertTravelRouteMenuConf = {
  key: 'insertTravelRoute',
  factory() {
    return new InsertTravelRouteMenu()
  }
}

// 默认导出
export default insertTravelRouteMenuConf 