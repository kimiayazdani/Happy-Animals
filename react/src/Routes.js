import React, { Component } from "react";
import {BrowserRouter as Router, Switch, Route } from "react-router-dom";

import SignUp from "./Pages/SignUp";
import Login from "./Pages/Login";
import Posts from "./Pages/Posts";
import Forum from "./Pages/Forum";
import Logout from "./Pages/Logout";

// import history from './history';


class Routes extends Component {
    render() {
        return (
            <Router>
                <Switch>
                    <Route path="/" exact component={Login} />
                    <Route path="/SignUp" component={SignUp} />
                    <Route path="/Posts" component={Posts} />
                    <Route path="/Forum" component={Forum} />
                    <Route path="/Logout" component={Logout} />
                </Switch>
            </Router>


        )
    }
}

export default Routes;