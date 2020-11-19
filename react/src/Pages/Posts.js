import React, { Component } from "react";
import axios from "axios"; 
import {Logger, ConsoleLogger} from 'react-console-logger';
import SideMenu from './../Components/SideMenu';
import './Notfound.css';
import { Divider, Image } from 'semantic-ui-react'

import "semantic-ui-css/semantic.min.css";

import {
  Button,
  Form,
  Grid,
  Header,
  Message,
  Segment
} from "semantic-ui-react";

import "./Posts.css";

class Posts extends Component {

  state = {
    title:"واگذاری سگ هاسکی",
    labels : ["سگ","نر","هاسکی"],
    image:"/static/images/wolf.jpg",
    description:"کاملا آموزش دیدست و جای دست‌شوییشو بلده، خیلی مهربونه و به محبت نیاز داره خیلی شیطونه و\n" +
        "                              همش بپر بپر میکنه اما بچه‌ی مودبیه و وقتی خونه نیستیم پارس نمیکنه. به همراه قلاده و پت\n" +
        "                              کریر و اسباب بازی‌های مورد علاقش واگذار میشه",
  };
  handleSubmit = (e) => { 
      e.preventDefault(); 

      axios 
          .post("http://localhost:8000/api/v1/post/overview", {
              title: this.state.title,
              image: this.state.image,
              labels: this.state.labels,
              description: this.state.description,
          })
          .then((res) => { 
              this.setState({ 
                  title: "",
                  image: "",
                  labels: "",
                  description: "",
              });
          }) 
          .catch((err) => {}); 
  }; 
  render() {
    return (
      <div className="App">
      <SideMenu redirectto={1} namepage={'Posts'}/>
        <Grid textAlign="center" verticalAlign="top">
          <Grid.Column style={{ maxWidth: 700 }}>
            <Form size="large">
              <Segment>
                  <div>
                      <div className="header" > { this.state.title }</div>
                      <Image src={ this.state.image } className={"ui small circular image centered"} />{""}

                      <div className="ui aligned container">
                          <p>{ this.state.description }</p>
                      </div>
                      <div className="ui labeled icon three item horizental menu">
                          <a className="item"> <i className="like icon"></i> پسندیدم </a>
                          <a className="item"> <i className="add icon"></i> تحت نظر </a>
                          <a className="item"> <i className="user circle icon"></i>مشاهده کاربر </a>
                      </div>
                  </div>
              </Segment>
            </Form>
          </Grid.Column>
        </Grid>
      </div>
    );
  }
}

export default Posts;

