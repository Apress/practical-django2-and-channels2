import React, { Component } from 'react'
import {
  StyleSheet,
  Text,
  View,
  TouchableHighlight,
  TextInput
} from 'react-native'

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center'
  },
  welcome: {
    fontSize: 20,
    textAlign: 'center',
    margin: 10
  },
  instructions: {
    textAlign: 'center',
    color: '#333333',
    marginBottom: 5
  },
  input: {
    height: 40,
    fontSize: 18,
    width: 150
  },
  button: {
    padding: 10
  }
})

export default class LoginView extends Component {
  constructor (props) {
    super(props)
    this.state = {
      username: '',
      password: ''
    }
    this.handleSubmitLogin = this.handleSubmitLogin.bind(this)
  }

  handleSubmitLogin () {
    if (this.state.username && this.state.password) {
      return this.props.backendApi
        .auth(this.state.username, this.state.password)
        .then(loggedIn => {
          if (loggedIn) {
            this.props.setLoggedIn()
          } else {
            this.setState({
              username: '',
              password: ''
            })
            alert('Login unsuccessful')
          }
        })
    }
  }

  render () {
    return (
      <View style={styles.container}>
        <Text style={styles.welcome}>BookTime</Text>
        <Text style={styles.instructions}>Please login to see your orders</Text>
        <TextInput
          style={styles.input}
          placeholder="Username"
          value={this.state.username}
          onChangeText={text => {
            this.setState({ username: text })
          }}
        />
        <TextInput
          style={styles.input}
          placeholder="Password"
          value={this.state.password}
          secureTextEntry={true}
          onChangeText={text => {
            this.setState({ password: text })
          }}
        />
        <TouchableHighlight
          style={styles.button}
          onPress={this.handleSubmitLogin}
        >
          <Text>Submit</Text>
        </TouchableHighlight>
      </View>
    )
  }
}
