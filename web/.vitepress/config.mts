import { defineConfig } from 'vitepress'
import { withMermaid } from 'vitepress-plugin-mermaid'

export default withMermaid(
  defineConfig({
    title: 'Engineering Report Stack',
    description: 'Traceable Report-as-Code for engineering WebUI reports',
    cleanUrls: true,
    themeConfig: {
      nav: [
        { text: 'Home', link: '/' },
        { text: 'Demo Report', link: '/generated/demo-report' },
        { text: 'Architecture', link: '/guide/architecture' },
        { text: 'GitHub', link: 'https://github.com/Tunglam0605/Engineering-Report-Stack' }
      ],
      sidebar: [
        {
          text: 'Engineering Report Stack',
          items: [
            { text: 'Overview', link: '/' },
            { text: 'Architecture', link: '/guide/architecture' },
            { text: 'Demo Report', link: '/generated/demo-report' }
          ]
        }
      ],
      socialLinks: [
        { icon: 'github', link: 'https://github.com/Tunglam0605/Engineering-Report-Stack' }
      ],
      search: {
        provider: 'local'
      }
    },
    mermaid: {
      securityLevel: 'strict'
    }
  })
)
