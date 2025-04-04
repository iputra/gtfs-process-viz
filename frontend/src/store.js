import { createStore, combineReducers, applyMiddleware } from "redux";
import { keplerGlReducer } from "kepler.gl/reducers";

const reducers = combineReducers({
  keplerGl: keplerGlReducer,
});

// Create store with middleware
export default createStore(reducers, {});
