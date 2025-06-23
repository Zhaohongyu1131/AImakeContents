/**
 * Register Page Component
 * 注册页面组件 - [Register][Page]
 */

import React from 'react'
import { Form, Input, Button, Typography, Space, Divider, message } from 'antd'
import { UserOutlined, LockOutlined, MailOutlined, PhoneOutlined } from '@ant-design/icons'
import { Link, useNavigate } from 'react-router-dom'

const { Text } = Typography

interface RegisterFormValues {
  username: string
  email: string
  phone?: string
  password: string
  confirmPassword: string
}

const RegisterPage: React.FC = () => {
  const navigate = useNavigate()
  const [form] = Form.useForm()
  const [loading, setLoading] = React.useState(false)

  const handleSubmit = async (values: RegisterFormValues) => {
    setLoading(true)
    try {
      // TODO: 实现注册逻辑
      console.log('Register values:', values)
      
      // 模拟注册成功
      await new Promise(resolve => setTimeout(resolve, 1000))
      message.success('注册成功，请登录')
      navigate('/auth/login', { replace: true })
    } catch (error) {
      message.error('注册失败，请稍后重试')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <Form
        form={form}
        name="register"
        onFinish={handleSubmit}
        autoComplete="off"
        size="large"
      >
        <Form.Item
          name="username"
          rules={[
            { required: true, message: '请输入用户名' },
            { min: 3, message: '用户名至少3位字符' },
            { max: 20, message: '用户名最多20位字符' },
          ]}
        >
          <Input
            prefix={<UserOutlined />}
            placeholder="用户名"
          />
        </Form.Item>

        <Form.Item
          name="email"
          rules={[
            { required: true, message: '请输入邮箱地址' },
            { type: 'email', message: '请输入有效的邮箱地址' },
          ]}
        >
          <Input
            prefix={<MailOutlined />}
            placeholder="邮箱地址"
          />
        </Form.Item>

        <Form.Item
          name="phone"
          rules={[
            { pattern: /^1[3-9]\d{9}$/, message: '请输入有效的手机号码' },
          ]}
        >
          <Input
            prefix={<PhoneOutlined />}
            placeholder="手机号码（可选）"
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

        <Form.Item
          name="confirmPassword"
          dependencies={['password']}
          rules={[
            { required: true, message: '请确认密码' },
            ({ getFieldValue }) => ({
              validator(_, value) {
                if (!value || getFieldValue('password') === value) {
                  return Promise.resolve()
                }
                return Promise.reject(new Error('两次输入的密码不一致'))
              },
            }),
          ]}
        >
          <Input.Password
            prefix={<LockOutlined />}
            placeholder="确认密码"
          />
        </Form.Item>

        <Form.Item>
          <Button
            type="primary"
            htmlType="submit"
            loading={loading}
            style={{ width: '100%' }}
          >
            注册
          </Button>
        </Form.Item>
      </Form>

      <Divider>或</Divider>

      <Space direction="vertical" style={{ width: '100%', textAlign: 'center' }}>
        <Text type="secondary">已有账号？</Text>
        <Link to="/auth/login">
          <Button type="link" style={{ padding: 0 }}>
            立即登录
          </Button>
        </Link>
      </Space>
    </div>
  )
}

export default RegisterPage