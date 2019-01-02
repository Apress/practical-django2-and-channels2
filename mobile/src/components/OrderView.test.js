import React from 'react'
import OrderView from './OrderView'

import renderer from 'react-test-renderer'

it('renders without crashing', () => {
  const mockOrders = [{ id: 5, image: null, summary: '2xaa', price: 22 }]
  const backendApi = {
    fetchOrders: jest.fn(
      () => new Promise((resolve, reject) => resolve(mockOrders))
    ),
    createAbsUrl: jest.fn(url => 'http://booktime.domain' + url)
  }
  const rendered = renderer.create(<OrderView backendApi={backendApi} />)
  expect(rendered).toBeTruthy()
  expect(backendApi.fetchOrders.mock.calls.length).toBe(1)
  rendered.getInstance().setOrders(mockOrders)
  expect(rendered.getInstance().state.orders).toBe(mockOrders)
  expect(rendered.toJSON()).toMatchSnapshot()
})
