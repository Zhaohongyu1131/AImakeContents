/**
 * Application Global Store
 * 应用全局状态管理 - [app][store]
 */

import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export interface AppState {
  // 主题配置
  theme: 'light' | 'dark'
  
  // 语言配置
  locale: string
  
  // 布局配置
  layout: {
    siderCollapsed: boolean
    headerHeight: number
    siderWidth: number
  }
  
  // 用户偏好
  preferences: {
    autoSave: boolean
    showTips: boolean
    defaultFileFormat: string
  }
}

export interface AppActions {
  // 主题操作
  appThemeSet: (theme: 'light' | 'dark') => void
  appThemeToggle: () => void
  
  // 语言操作
  appLocaleSet: (locale: string) => void
  
  // 布局操作
  appLayoutSiderToggle: () => void
  appLayoutSiderCollapsedSet: (collapsed: boolean) => void
  
  // 偏好设置操作
  appPreferencesUpdate: (preferences: Partial<AppState['preferences']>) => void
  
  // 重置应用状态
  appStateReset: () => void
}

const initialState: AppState = {
  theme: 'light',
  locale: 'zh-CN',
  layout: {
    siderCollapsed: false,
    headerHeight: 64,
    siderWidth: 256,
  },
  preferences: {
    autoSave: true,
    showTips: true,
    defaultFileFormat: 'wav',
  },
}

export const useAppStore = create<AppState & AppActions>()(
  persist(
    (set, get) => ({
      ...initialState,
      
      // 主题操作
      appThemeSet: (theme) =>
        set({ theme }),
      
      appThemeToggle: () => {
        const currentTheme = get().theme
        set({ theme: currentTheme === 'light' ? 'dark' : 'light' })
      },
      
      // 语言操作
      appLocaleSet: (locale) =>
        set({ locale }),
      
      // 布局操作
      appLayoutSiderToggle: () => {
        const { layout } = get()
        set({
          layout: {
            ...layout,
            siderCollapsed: !layout.siderCollapsed,
          },
        })
      },
      
      appLayoutSiderCollapsedSet: (collapsed) => {
        const { layout } = get()
        set({
          layout: {
            ...layout,
            siderCollapsed: collapsed,
          },
        })
      },
      
      // 偏好设置操作
      appPreferencesUpdate: (newPreferences) => {
        const { preferences } = get()
        set({
          preferences: {
            ...preferences,
            ...newPreferences,
          },
        })
      },
      
      // 重置应用状态
      appStateReset: () =>
        set(initialState),
    }),
    {
      name: 'datasay-app-store',
      partialize: (state) => ({
        theme: state.theme,
        locale: state.locale,
        layout: state.layout,
        preferences: state.preferences,
      }),
    }
  )
)