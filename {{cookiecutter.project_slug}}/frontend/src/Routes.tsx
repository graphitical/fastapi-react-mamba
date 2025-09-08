import { makeStyles } from '@material-ui/core/styles';
import React, { FC } from 'react';
import { useHistory } from 'react-router';
import { Route, Switch } from 'react-router-dom';

import { Admin } from './admin';
import { logout } from './utils/auth';
import { Home, Login, PrivateRoute, Protected, SignUp } from './views';

const useStyles = makeStyles((theme) => ({
  app: {
    textAlign: 'center',
  },
  header: {
    backgroundColor: '#282c34',
    minHeight: '100vh',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: 'calc(10px + 2vmin)',
    color: 'white',
  },
}));

export const Routes: FC = () => {
  const classes = useStyles();
  const history = useHistory();

  return (
    <div className={classes.app}>
      <header className={classes.header}>
        <Switch>
          <Route path="/admin">
            <Admin />
          </Route>
          <Route path="/login" component={Login} />
          <Route path="/signup" component={SignUp} />
          <Route
            path="/logout"
            render={() => {
              logout();
              history.push('/');
              return null;
            }}
          />
          <PrivateRoute path="/protected" component={Protected} />
          <Route exact path="/" component={Home} />
        </Switch>
      </header>
    </div>
  );
};