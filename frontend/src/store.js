import { createStore, combineReducers, applyMiddleware } from 'redux';
import { enhanceReduxMiddleware } from 'react-palm/middleware';
import keplerGlReducer from 'kepler.gl/reducers';

const reducers = combineReducers({
  keplerGl: keplerGlReducer
});

// Create store with middleware
export default createStore(
  reducers,
  {},
  applyMiddleware(enhanceReduxMiddleware())
);
