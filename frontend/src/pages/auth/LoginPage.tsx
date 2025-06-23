/**
 * Login Page Component
 * 登录页面组件 - [Login][Page]
 */

import React from 'react'
import { Form, Input, Button, Checkbox, Typography, Space, Divider, message } from 'antd'
import { UserOutlined, LockOutlined } from '@ant-design/icons'
import { Link, useNavigate } from 'react-router-dom'

const { Text } = Typography

interface LoginFormValues {
  email: string
  password: string
  remember: boolean
}

const LoginPage: React.FC = () => {
  const navigate = useNavigate()
  const [form] = Form.useForm()
  const [loading, setLoading] = React.useState(false)

  const handleSubmit = async (values: LoginFormValues) => {
    setLoading(true)
    try {
      // TODO: 实现登录逻辑
      console.log('Login values:', values)
      
      // 模拟登录成功
      await new Promise(resolve => setTimeout(resolve, 1000))
      message.success('登录成功')
      navigate('/', { replace: true })
    } catch (error) {
      message.error('登录失败，请检查用户名和密码')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <Form
        form={form}
        name="login"
        onFinish={handleSubmit}
        autoComplete="off"
        size="large"
      >
        <Form.Item
          name="email"
          rules={[
            { required: true, message: '请输入邮箱地址' },
            { type: 'email', message: '请输入有效的邮箱地址' },
          ]}
        >
          <Input
            prefix={<UserOutlined />}
            placeholder="邮箱地址"
          />
        </Form.Item>

        <Form.Item
          name="password"
          rules={[
            { required: true, message: '请输入密码' },
            { min: 6, message: '密码至少6位字符' },
          ]}
        >
          <Input.Password
            prefix={<LockOutlined />}
            placeholder="密码"
          />
        </Form.Item>

        <Form.Item>
          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <Form.Item name="remember" valuePropName="checked" noStyle>
              <Checkbox>记住我</Checkbox>
            </Form.Item>
            <Link to="/auth/forgot">忘记密码？</Link>
          </div>
        </Form.Item>

        <Form.Item>
          <Button
            type="primary"
            htmlType="submit"
            loading={loading}
            style={{ width: '100%' }}
          >
            登录
          </Button>
        </Form.Item>
      </Form>

      <Divider>或</Divider>

      <Space direction="vertical" style={{ width: '100%', textAlign: 'center' }}>
        <Text type="secondary">还没有账号？</Text>
        <Link to="/auth/register">
          <Button type="link" style={{ padding: 0 }}>
            立即注册
          </Button>
        </Link>
      </Space>
    </div>
  )
}

export default LoginPage