import React from 'react'
import ChatView from './ChatView'

import renderer from 'react-test-renderer'

it('renders without orders specified', () => {
  const rendered = renderer.create(<ChatView />).toJSON()
  expect(rendered).toBeTruthy()
})

it('renders with orders specified', () => {
  const backendApi = {
    openMessagesStream: jest.fn(),
    closeMessagesStream: jest.fn(),
    sendMessage: jest.fn(),
    fetchShipmentStatus: jest.fn(
      () => new Promise((resolve, reject) => resolve())
    ),
  }
  const rendered = renderer.create(
    <ChatView backendApi={backendApi} orderCurrentId="1" />
  )
  rendered.root.instance.componentDidUpdate({})
  expect(backendApi.openMessagesStream.mock.calls.length).toBe(1)
  expect(backendApi.openMessagesStream.mock.calls[0][0]).toBe('1')
  expect(backendApi.fetchShipmentStatus.mock.calls.length).toBe(1)
  expect(backendApi.fetchShipmentStatus.mock.calls[0][0]).toBe('1')
  rendered.getInstance().setState({shipmentStatus: 'shipped'})
  backendApi.openMessagesStream.mock.calls[0][1]('initial message')
  expect(rendered.toJSON()).toMatchSnapshot()

  rendered.root.instance.handleSubmit({ nativeEvent: { text: 'answer back' } })
  expect(backendApi.sendMessage.mock.calls.length).toBe(1)
  expect(backendApi.sendMessage.mock.calls[0][0]).toBe('answer back')
  expect(rendered.toJSON()).toMatchSnapshot()
})
