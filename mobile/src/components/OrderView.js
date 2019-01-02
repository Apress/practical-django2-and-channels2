import React from 'react'
import {
  StyleSheet,
  Text,
  Image,
  TouchableHighlight,
  TouchableOpacity,
  View
} from 'react-native'

import ChatView from './ChatView'

const styles = StyleSheet.create({
  container: {
    paddingTop: 25,
    flex: 1
  },
  orderContainer: {
    borderColor: 'blue',
    borderWidth: 1,
    height: 200
  },
  orderRowOut: {
    borderColor: 'yellow',
    borderWidth: 1,
    height: 52
  },
  orderRowIn: {
    flex: 1,
    flexDirection: 'row',
    alignSelf: 'stretch'
  },
  orderSelected: {
    backgroundColor: 'lightgrey'
  },
  orderImage: {
    borderColor: 'green',
    borderWidth: 1,
    width: 50,
    height: 50
  },
  orderSummary: {
    borderColor: 'red',
    borderWidth: 1,
    flex: 1,
    alignSelf: 'stretch'
  },
  orderPrice: {
    borderColor: 'blue',
    borderWidth: 1
  }
})

function OrderImage (props) {
  if (props.image) {
    return (
      <Image
        style={{ width: 50, height: 50 }}
        source={{ uri: props.backendApi.create_abs_url(props.image) }}
      />
    )
  } else {
    return <View />
  }
}

function OrderTouchArea (props) {
  return (
    <View
      style={[
        styles.orderRowIn,
        props.order.id == props.orderCurrentId ? styles.orderSelected : null
      ]}
    >
      <View style={styles.orderImage}>
        <OrderImage backendApi={props.backendApi} image={props.order.image} />
      </View>
      <Text style={styles.orderSummary}>{props.order.summary}</Text>
      <Text style={styles.orderPrice}>{props.order.price}</Text>
    </View>
  )
}

function OrderSingleView (props) {
  return (
    <TouchableHighlight
      style={styles.orderRowOut}
      onPress={() => props.setOrderId(props.order.id)}
    >
      <OrderTouchArea
        backendApi={props.backendApi}
        order={props.order}
        orderCurrentId={props.orderCurrentId}
      />
    </TouchableHighlight>
  )
}

export default class OrderView extends React.Component {
  constructor (props) {
    super(props)
    this.state = {
      orders: [],
      orderCurrentId: null
    }
  }

  componentDidMount () {
    this.props.backendApi
      .fetchOrders()
      .then(orders => this.setOrders(orders))
      .catch(() => alert('Error fetching orders'))
  }

  setOrders (orders) {
    this.setState({
      orders: orders
    })
  }

  render () {
    return (
      <View style={styles.container}>
        <View style={styles.orderContainer}>
          <Text>Your BookTime orders</Text>
          {this.state.orders.map(m => (
            <OrderSingleView
              backendApi={this.props.backendApi}
              key={m.id}
              order={m}
              orderCurrentId={this.state.orderCurrentId}
              setOrderId={orderId => this.setState({ orderCurrentId: orderId })}
            />
          ))}
        </View>
        <ChatView
          backendApi={this.props.backendApi}
          orderCurrentId={this.state.orderCurrentId}
        />
      </View>
    )
  }
}
