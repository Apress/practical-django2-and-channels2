import React from 'react'
import LoginView from './src/components/LoginView'
import ChatView from './src/components/ChatView'
import OrderView from './src/components/OrderView'
import BackendApi from './src/backend'

export default class App extends React.Component {
  constructor (props) {
    super(props)
    this.backendApi = new BackendApi()
    this.state = {
      loggedIn: false
    }
  }

  render () {
    if (this.state.loggedIn) {
      return <OrderView backendApi={this.backendApi} />
    } else {
      return (
        <LoginView
          backendApi={this.backendApi}
          setLoggedIn={() => this.setState({ loggedIn: true })}
        />
      )
    }
  }
}
