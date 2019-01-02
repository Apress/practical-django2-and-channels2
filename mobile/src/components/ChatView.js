import React from 'react'
import { StyleSheet, Text, TextInput, ScrollView, View } from 'react-native'

const styles = StyleSheet.create({
  chatContainer: {
    borderColor: 'orange',
    borderWidth: 1,
    flex: 1
  },
  chatMessages: {
    borderColor: 'purple',
    borderWidth: 1,
    flex: 1
  },
  chatInput: {
    height: 40,
    margin: 10,
    borderWidth: 1
  },
  chatMessage: {
    backgroundColor: 'lightgrey',
    margin: 10,
    flex: 1,
    flexDirection: 'row',
    alignSelf: 'stretch'
  },
  chatMessageText: {
    flex: 1
  },
  chatMessageType: {
    flex: 1,
    textAlign: 'right'
  }
})

export default class ChatView extends React.Component {
  constructor (props) {
    super(props)
    this.state = {
      messages: [],
      shipmentStatus: "n/a"
    }
    this.handleSubmit = this.handleSubmit.bind(this)
  }

  componentDidUpdate (prevProps) {
    if (prevProps.orderCurrentId !== this.props.orderCurrentId) {
      this.props.backendApi.closeMessagesStream()
      this.state = {
        messages: []
      }
      this.props.backendApi
        .fetchShipmentStatus(this.props.orderCurrentId)
        .then(result => {
            this.setState({shipmentStatus: result})
        })
      this.props.backendApi.openMessagesStream(
        this.props.orderCurrentId,
        message => {
          this.setState({
            messages: this.state.messages.concat([message])
          })
        }
      )
    }
  }

  handleSubmit (event) {
    var text = event.nativeEvent.text
    this.props.backendApi.sendMessage(text)
    this.refs.textInput.setNativeProps({ text: '' })
  }

  render () {
    if (this.props.orderCurrentId) {
      return (
        <View style={styles.chatContainer}>
          <Text>Chat for order: {this.props.orderCurrentId}
          - {this.state.shipmentStatus}</Text>
          <ScrollView
            style={styles.chatMessages}
            showsVerticalScrollIndicator={true}
            ref={ref => (this.scrollView = ref)}
            onContentSizeChange={(contentWidth, contentHeight) => {
              this.scrollView.scrollToEnd({ animated: true })
            }}
          >
            {this.state.messages.map((m, index) => {
              return (
                <View key={index} style={styles.chatMessage}>
                  <Text style={styles.chatMessageText}>
                    {m.username} {m.message}
                  </Text>
                  <Text style={styles.chatMessageType}>{m.type}</Text>
                </View>
              )
            })}
          </ScrollView>
          <TextInput
            style={styles.chatInput}
            ref="textInput"
            placeholder="Enter a message..."
            returnKeyType="send"
            onSubmitEditing={this.handleSubmit}
          />
        </View>
      )
    } else {
      return (
        <View>
          <Text>No order selected for chat</Text>
        </View>
      )
    }
  }
}
