import React from 'react'
import LoginView from './LoginView'

import renderer from 'react-test-renderer'

it('renders without crashing', () => {
  const rendered = renderer.create(<LoginView />)
  expect(rendered).toBeTruthy()
})

it('logins successfully when backend returns true', () => {
  const setLoggedIn = jest.fn()
  const backendApi = {
    auth: jest.fn(() => new Promise((resolve, reject) => resolve(true)))
  }
  const rendered = renderer.create(
    <LoginView backendApi={backendApi} setLoggedIn={setLoggedIn} />
  )
  rendered.root.instance.state.username = 'a'
  rendered.root.instance.state.password = 'b'
  rendered.root.instance
    .handleSubmitLogin()
    .then(() => expect(setLoggedIn.mock.calls.length).toBe(1))
  expect(backendApi.auth.mock.calls.length).toBe(1)
  expect(backendApi.auth.mock.calls[0][0]).toBe('a')
  expect(backendApi.auth.mock.calls[0][1]).toBe('b')
})

it('login fails when backend returns false', () => {
  const setLoggedIn = jest.fn()
  const backendApi = {
    auth: jest.fn(() => new Promise((resolve, reject) => resolve(false)))
  }
  const rendered = renderer.create(
    <LoginView backendApi={backendApi} setLoggedIn={setLoggedIn} />
  )
  rendered.root.instance.state.username = 'a'
  rendered.root.instance.state.password = 'b'
  rendered.root.instance
    .handleSubmitLogin()
    .then(() => expect(setLoggedIn.mock.calls.length).toBe(0))
  expect(backendApi.auth.mock.calls.length).toBe(1)
  expect(backendApi.auth.mock.calls[0][0]).toBe('a')
  expect(backendApi.auth.mock.calls[0][1]).toBe('b')
})

it('login fails when backend fails', () => {
  const setLoggedIn = jest.fn()
  const backendApi = {
    auth: jest.fn(() => new Promise((resolve, reject) => reject()))
  }
  const rendered = renderer.create(
    <LoginView backendApi={backendApi} setLoggedIn={setLoggedIn} />
  )
  rendered.root.instance.state.username = 'a'
  rendered.root.instance.state.password = 'b'
  rendered.root.instance
    .handleSubmitLogin()
    .then(() => expect(setLoggedIn.mock.calls.length).toBe(0))
  expect(backendApi.auth.mock.calls.length).toBe(1)
  expect(backendApi.auth.mock.calls[0][0]).toBe('a')
  expect(backendApi.auth.mock.calls[0][1]).toBe('b')
})
