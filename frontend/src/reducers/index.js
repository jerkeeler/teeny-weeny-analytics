import { combineReducers } from 'redux';
import { fromJS } from 'immutable';


const initialState = fromJS({
  ui: {},
  data: {},
});
const defaultReducer = (state = initialState) => state;

const rootReducer = combineReducers({
  defaultReducer,
});

export default rootReducer;
