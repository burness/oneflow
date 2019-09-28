#ifndef ONEFLOW_CORE_DATA_DATA_INSTANCE_H_
#define ONEFLOW_CORE_DATA_DATA_INSTANCE_H_

#include "oneflow/core/data/data_field.h"

namespace oneflow {
namespace data {

class DataInstance {
 public:
  DataInstance() = default;
  DataInstance(const DataInstanceProto& proto);

  template<DataSourceCase dsrc, typename... Args>
  DataField* GetOrCreateField(Args&&... args);

  template<DataSourceCase dsrc>
  DataField* GetField();
  DataField* GetField(DataSourceCase dsrc);
  template<DataSourceCase dsrc>
  const DataField* GetField() const;
  const DataField* GetField(DataSourceCase dsrc) const;
  template<DataSourceCase dsrc>
  bool HasField() const;
  bool AddField(std::unique_ptr<DataField>&& data_field_ptr);
  void Transform(const DataTransformProto& trans_proto);

 private:
  HashMap<DataSourceCase, std::unique_ptr<DataField>, std::hash<int>> fields_;
};

inline const DataField* DataInstance::GetField(DataSourceCase dsrc) const {
  return const_cast<const DataField*>(fields_.at(dsrc).get());
}

inline DataField* DataInstance::GetField(DataSourceCase dsrc) { return fields_.at(dsrc).get(); }

template<DataSourceCase dsrc>
inline DataField* DataInstance::GetField() {
  return fields_.at(dsrc).get();
}

template<DataSourceCase dsrc>
inline const DataField* DataInstance::GetField() const {
  return const_cast<const DataField*>(fields_.at(dsrc).get());
}

template<DataSourceCase dsrc>
inline bool DataInstance::HasField() const {
  return fields_.find(dsrc) != fields_.end();
}

inline bool DataInstance::AddField(std::unique_ptr<DataField>&& data_field_ptr) {
  return fields_.emplace(data_field_ptr->Source(), std::move(data_field_ptr)).second;
}

}  // namespace data
}  // namespace oneflow

#endif  // ONEFLOW_CORE_DATA_DATA_INSTANCE_H_